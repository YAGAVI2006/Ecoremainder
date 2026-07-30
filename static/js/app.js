/**
 * EcoReminder Frontend Client Logic & Interactive Maps
 */

document.addEventListener('DOMContentLoaded', () => {
  initToasts();
  initTableSearchAndFilters();
  initImagePreviews();
});

// Toast Auto-Dismiss
function initToasts() {
  const toastElList = document.querySelectorAll('.toast');
  toastElList.forEach((toastEl) => {
    const toast = new bootstrap.Toast(toastEl, { delay: 4000 });
    toast.show();
  });
}

// Client-side Table Search & Status Tab Filtering
function initTableSearchAndFilters() {
  const searchInput = document.getElementById('tableSearchInput');
  const filterTabs = document.querySelectorAll('[data-filter-status]');
  const tableRows = document.querySelectorAll('.filterable-table tbody tr');

  if (!tableRows.length) return;

  let activeStatus = 'all';
  let searchQuery = '';

  const applyFilters = () => {
    tableRows.forEach((row) => {
      const rowStatus = (row.getAttribute('data-status') || '').toLowerCase();
      const rowText = row.textContent.toLowerCase();

      const matchesStatus = activeStatus === 'all' || rowStatus === activeStatus;
      const matchesSearch = !searchQuery || rowText.includes(searchQuery);

      if (matchesStatus && matchesSearch) {
        row.style.display = '';
      } else {
        row.style.display = 'none';
      }
    });
  };

  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      searchQuery = e.target.value.toLowerCase().trim();
      applyFilters();
    });
  }

  filterTabs.forEach((tab) => {
    tab.addEventListener('click', (e) => {
      e.preventDefault();
      filterTabs.forEach((t) => t.classList.remove('active', 'btn-eco-primary'));
      filterTabs.forEach((t) => t.classList.add('btn-outline-secondary'));

      tab.classList.remove('btn-outline-secondary');
      tab.classList.add('active', 'btn-eco-primary');

      activeStatus = tab.getAttribute('data-filter-status').toLowerCase();
      applyFilters();
    });
  });
}

// Image File Upload Preview
function initImagePreviews() {
  const fileInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
  fileInputs.forEach((input) => {
    input.addEventListener('change', function () {
      const file = this.files[0];
      if (!file) return;

      const previewId = this.getAttribute('data-preview-target');
      if (!previewId) return;

      const previewEl = document.getElementById(previewId);
      if (!previewEl) return;

      const reader = new FileReader();
      reader.onload = (e) => {
        previewEl.src = e.target.result;
        previewEl.classList.remove('d-none');
      };
      reader.readAsDataURL(file);
    });
  });
}

/**
 * Interactive Leaflet Map Picker for Report Form
 */
function initReportMapPicker(containerId, latId, lngId, addressId, detectBtnId) {
  const container = document.getElementById(containerId);
  if (!container || typeof L === 'undefined') return;

  const latInput = document.getElementById(latId);
  const lngInput = document.getElementById(lngId);
  const addressInput = document.getElementById(addressId);
  const detectBtn = document.getElementById(detectBtnId);

  // Default coordinate (NYC center or default city)
  let defaultLat = 40.7589;
  let defaultLng = -73.9851;

  if (latInput.value && lngInput.value) {
    defaultLat = parseFloat(latInput.value);
    defaultLng = parseFloat(lngInput.value);
  }

  const map = L.map(containerId).setView([defaultLat, defaultLng], 14);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap contributors',
  }).addTo(map);

  let marker = L.marker([defaultLat, defaultLng], { draggable: true }).addTo(map);

  function updateCoords(lat, lng, doReverseGeocode = true) {
    latInput.value = lat.toFixed(6);
    lngInput.value = lng.toFixed(6);
    marker.setLatLng([lat, lng]);

    if (doReverseGeocode) {
      reverseGeocode(lat, lng);
    }
  }

  marker.on('dragend', function (e) {
    const position = marker.getLatLng();
    updateCoords(position.lat, position.lng);
  });

  map.on('click', function (e) {
    updateCoords(e.latlng.lat, e.latlng.lng);
  });

  function reverseGeocode(lat, lng) {
    fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`)
      .then((res) => res.json())
      .then((data) => {
        if (data && data.display_name && addressInput && !addressInput.value.trim()) {
          addressInput.value = data.display_name;
        }
      })
      .catch(() => {});
  }

  if (detectBtn) {
    detectBtn.addEventListener('click', () => {
      if (!navigator.geolocation) {
        alert('Geolocation is not supported by your browser.');
        return;
      }
      detectBtn.disabled = true;
      detectBtn.innerHTML = '<i class="bi bi-arrow-repeat spin"></i> Detecting...';

      navigator.geolocation.getCurrentPosition(
        (position) => {
          const lat = position.coords.latitude;
          const lng = position.coords.longitude;
          map.setView([lat, lng], 16);
          updateCoords(lat, lng, true);

          detectBtn.disabled = false;
          detectBtn.innerHTML = '<i class="bi bi-geo-alt-fill"></i> Location Detected';
        },
        (error) => {
          detectBtn.disabled = false;
          detectBtn.innerHTML = '<i class="bi bi-geo-alt"></i> Detect My Location';
          alert('Unable to retrieve your location. Please select manually on the map.');
        }
      );
    });
  }
}

/**
 * Interactive System Map for Admin & Dashboards
 */
function initComplaintsMap(containerId, apiEndpoint = '/api/complaints') {
  const container = document.getElementById(containerId);
  if (!container || typeof L === 'undefined') return;

  fetch(apiEndpoint)
    .then((res) => res.json())
    .then((complaints) => {
      const validComplaints = complaints.filter((c) => c.latitude && c.longitude);
      if (!validComplaints.length) {
        container.innerHTML =
          '<div class="d-flex h-100 align-items-center justify-content-center text-muted">No bin locations mapped yet.</div>';
        return;
      }

      const centerLat = validComplaints[0].latitude;
      const centerLng = validComplaints[0].longitude;

      const map = L.map(containerId).setView([centerLat, centerLng], 12);

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '© OpenStreetMap',
      }).addTo(map);

      const bounds = [];

      validComplaints.forEach((c) => {
        const markerColor =
          c.status === 'Collected' ? '#059669' : c.status === 'In Progress' ? '#0284c7' : '#d97706';

        const customHtmlIcon = L.divIcon({
          className: 'custom-map-pin',
          html: `<div style="background-color: ${markerColor}; width: 22px; height: 22px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 6px rgba(0,0,0,0.3);"></div>`,
          iconSize: [22, 22],
          iconAnchor: [11, 11],
        });

        const popupContent = `
          <div style="font-family: sans-serif; min-width: 180px;">
            <div style="font-weight: bold; margin-bottom: 4px;">Bin Report #${c.complaint_id}</div>
            <div style="font-size: 0.85rem; color: #555; margin-bottom: 6px;">${c.location}</div>
            <div style="margin-bottom: 6px;">
              <span class="badge" style="background:${markerColor}; color: white;">${c.status}</span>
            </div>
            ${c.description ? `<p style="font-size: 0.8rem; margin-bottom: 6px;">${c.description}</p>` : ''}
            ${c.collector_name ? `<div style="font-size:0.75rem; color:#666;">Collector: <strong>${c.collector_name}</strong></div>` : ''}
          </div>
        `;

        const marker = L.marker([c.latitude, c.longitude], { icon: customHtmlIcon }).addTo(map);
        marker.bindPopup(popupContent);

        bounds.push([c.latitude, c.longitude]);
      });

      if (bounds.length > 1) {
        map.fitBounds(bounds, { padding: [30, 30] });
      }
    })
    .catch((err) => console.error('Map loading error:', err));
}
