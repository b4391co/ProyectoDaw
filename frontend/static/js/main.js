// Elementos del DOM
const searchForm = document.getElementById('searchForm');
const startDateInput = document.getElementById('startDate');
const endDateInput = document.getElementById('endDate');
const searchTermInput = document.getElementById('searchTerm');
const keywordsInput = document.getElementById('keywords');
const severitySelect = document.getElementById('severity');
const formatJsonRadio = document.getElementById('formatJson');
const formatCsvRadio = document.getElementById('formatCsv');
const prettyJsonCheckbox = document.getElementById('prettyJson');
const customDelimiterCheckbox = document.getElementById('customDelimiter');
const delimiterContainer = document.getElementById('delimiterContainer');
const delimiterInput = document.getElementById('delimiter');
const searchResults = document.getElementById('searchResults');
const resultsContent = document.getElementById('resultsContent');

// Toast notification
const notificationToast = new bootstrap.Toast(document.getElementById('notificationToast'));
const toastTitle = document.getElementById('toastTitle');
const toastMessage = document.getElementById('toastMessage');

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    setupDateInputs();
});

function setupEventListeners() {
    // Event listener para el formulario
    searchForm.addEventListener('submit', handleFormSubmit);

    // Event listeners para los checkboxes
    customDelimiterCheckbox.addEventListener('change', () => {
        delimiterContainer.classList.toggle('d-none', !customDelimiterCheckbox.checked);
    });

    // Event listener para el formato CSV
    formatCsvRadio.addEventListener('change', () => {
        customDelimiterCheckbox.disabled = !formatCsvRadio.checked;
        if (!formatCsvRadio.checked) {
            customDelimiterCheckbox.checked = false;
            delimiterContainer.classList.add('d-none');
        }
    });

    // Event listener para el formato JSON
    formatJsonRadio.addEventListener('change', () => {
        prettyJsonCheckbox.disabled = !formatJsonRadio.checked;
        if (!formatJsonRadio.checked) {
            prettyJsonCheckbox.checked = false;
        }
    });
}

function setupDateInputs() {
    // Establecer fecha mínima y máxima
    const now = new Date();
    const oneYearAgo = new Date(now.getFullYear() - 1, now.getMonth(), now.getDate());
    
    startDateInput.min = oneYearAgo.toISOString().split('T')[0];
    startDateInput.max = now.toISOString().split('T')[0];
    
    endDateInput.min = oneYearAgo.toISOString().split('T')[0];
    endDateInput.max = now.toISOString().split('T')[0];
}

async function handleFormSubmit(event) {
    event.preventDefault();
    
    if (!validateForm()) {
        return;
    }

    try {
        const formData = getFormData();
        console.log('Enviando datos:', formData); // Log para depuración
        
        const response = await fetch('/api/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            const error = await response.json();
            console.error('Error de respuesta:', error); // Log para depuración
            throw new Error(error.detail || 'Error en la búsqueda');
        }

        const data = await response.json();
        console.log('Datos recibidos:', data); // Log para depuración
        
        // Si el formato es CSV, hacer una petición adicional para la conversión
        if (formData.format === 'csv') {
            const convertResponse = await fetch('/api/convert', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            if (!convertResponse.ok) {
                const error = await convertResponse.json();
                throw new Error(error.detail || 'Error en la conversión');
            }

            // Descargar el archivo CSV
            const blob = await convertResponse.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `nist_data_${new Date().toISOString()}.csv`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            showNotification('Éxito', 'Archivo CSV descargado correctamente', 'success');
        } else {
            // Mostrar resultados JSON
            showResults(data);
            showNotification('Éxito', 'Búsqueda completada correctamente', 'success');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error', error.message, 'danger');
    }
}

function validateForm() {
    const startDate = new Date(startDateInput.value);
    const endDate = new Date(endDateInput.value);

    if (startDate > endDate) {
        showNotification('Error', 'La fecha de inicio debe ser anterior a la fecha de fin', 'danger');
        return false;
    }

    if (formatCsvRadio.checked && customDelimiterCheckbox.checked && !delimiterInput.value) {
        showNotification('Error', 'Por favor, especifica un delimitador para CSV', 'danger');
        return false;
    }

    return true;
}

function getFormData() {
    return {
        start_date: `${startDateInput.value}T00:00:00`,
        end_date: `${endDateInput.value}T23:59:59`,
        search_term: searchTermInput.value || null,
        keywords: keywordsInput.value ? keywordsInput.value.split(',').map(k => k.trim()) : [],
        severity: severitySelect.value || null,
        format: formatJsonRadio.checked ? 'json' : 'csv',
        pretty: prettyJsonCheckbox.checked,
        delimiter: customDelimiterCheckbox.checked ? delimiterInput.value : ','
    };
}

function showResults(data) {
    searchResults.classList.remove('d-none');
    
    if (typeof data === 'string') {
        resultsContent.innerHTML = `<pre class="bg-light p-3 rounded">${data}</pre>`;
    } else {
        resultsContent.innerHTML = `<pre class="bg-light p-3 rounded">${JSON.stringify(data, null, 2)}</pre>`;
    }
}

function showNotification(title, message, type = 'info') {
    toastTitle.textContent = title;
    toastMessage.textContent = message;
    toastMessage.className = `toast-body text-${type}`;
    notificationToast.show();
} 