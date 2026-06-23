// Location autocomplete for search input fields
function initAutocomplete(inputSelector) {
    const input = document.querySelector(inputSelector);
    if (!input) return;

    // Create suggestion dropdown container
    const dropdown = document.createElement('div');
    dropdown.className = 'autocomplete-dropdown';
    dropdown.style.cssText = `
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        background: white;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        z-index: 1000;
        display: none;
        max-height: 250px;
        overflow-y: auto;
    `;

    // Wrap input in relative position container
    input.parentElement.style.position = 'relative';
    input.parentElement.appendChild(dropdown);

    let debounceTimer;

    input.addEventListener('input', function () {
        const query = this.value.trim();
        clearTimeout(debounceTimer);

        // Hide dropdown if query is too short
        if (query.length < 2) {
            dropdown.style.display = 'none';
            return;
        }

        // Wait 300ms after user stops typing before making API call
        debounceTimer = setTimeout(() => {
            fetch(`/api/locations/autocomplete/?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    dropdown.innerHTML = '';

                    if (data.length === 0) {
                        dropdown.style.display = 'none';
                        return;
                    }

                    // Build suggestion items
                    data.forEach(location => {
                        const item = document.createElement('div');
                        item.style.cssText = `
                            padding: 10px 15px;
                            cursor: pointer;
                            border-bottom: 1px solid #f0f0f0;
                            font-size: 0.95rem;
                            color:#333;
                        `;
                        item.innerHTML = `
                            <i class="fas fa-map-marker-alt me-2 text-danger"></i>
                            ${location.label}
                        `;

                        // Fill input with selected suggestion
                        item.addEventListener('click', () => {
                            input.value = location.city;
                            dropdown.style.display = 'none';
                            // Auto submit the form
                            input.closest('form').submit();
                        });

                        item.addEventListener('mouseover', () => {
                            item.style.background = '#f8f9fa';
                        });

                        item.addEventListener('mouseout', () => {
                            item.style.background = 'white';
                        });

                        dropdown.appendChild(item);
                    });

                    dropdown.style.display = 'block';
                })
                .catch(err => console.error('Autocomplete error:', err));
        }, 300);
    });

    // Hide dropdown when clicking outside
    document.addEventListener('click', function (e) {
        if (!input.parentElement.contains(e.target)) {
            dropdown.style.display = 'none';
        }
    });
}

// Initialize autocomplete on both homepage and property list search inputs
document.addEventListener('DOMContentLoaded', function () {
    initAutocomplete('input[name="search"]');
});