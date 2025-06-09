// Elementos del DOM
const searchForm = document.getElementById('searchForm');
const startDateInput = document.getElementById('startDate');
const endDateInput = document.getElementById('endDate');
const searchTermInput = document.getElementById('searchTerm');
const keywordsInput = document.getElementById('keywords');
const severitySelect = document.getElementById('severity');
const searchResults = document.getElementById('searchResults');
const resultsTableBody = document.getElementById('resultsTableBody');
const downloadJsonBtn = document.getElementById('downloadJson');
const downloadCsvBtn = document.getElementById('downloadCsv');

// Toast notification
const notificationToast = new bootstrap.Toast(document.getElementById('notificationToast'));
const toastTitle = document.getElementById('toastTitle');
const toastMessage = document.getElementById('toastMessage');

// Datos de la búsqueda actual
let currentSearchData = null;

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
    console.log('Inicializando aplicación...');
    setupEventListeners();
    setupDateInputs();
});

function setupEventListeners() {
    console.log('Configurando event listeners...');
    // Event listener para el formulario
    searchForm.addEventListener('submit', async (event) => {
        console.log('Formulario enviado');
        event.preventDefault(); // Prevenir la recarga de la página
        await handleFormSubmit(event);
    });
    
    // Event listeners para los botones de descarga
    downloadJsonBtn.addEventListener('click', () => downloadData('json'));
    downloadCsvBtn.addEventListener('click', () => downloadData('csv'));
}

function setupDateInputs() {
    console.log('Configurando fechas...');
    // Establecer fecha mínima y máxima
    const now = new Date();
    const oneYearAgo = new Date(now.getFullYear() - 1, now.getMonth(), now.getDate());
    
    startDateInput.min = oneYearAgo.toISOString().split('T')[0];
    startDateInput.max = now.toISOString().split('T')[0];
    
    endDateInput.min = oneYearAgo.toISOString().split('T')[0];
    endDateInput.max = now.toISOString().split('T')[0];

    // Establecer valores por defecto
    startDateInput.value = now.toISOString().split('T')[0];
    endDateInput.value = now.toISOString().split('T')[0];
}

async function handleFormSubmit(event) {
    console.log('Manejando envío del formulario...');
    
    if (!validateForm()) {
        console.log('Validación del formulario fallida');
        return;
    }

    try {
        const formData = getFormData();
        console.log('Enviando datos:', formData);
        
        const response = await fetch('/api/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        console.log('Respuesta recibida:', response.status);
        
        const data = await response.json();
        console.log('Datos recibidos:', data);
        
        if (!response.ok) {
            const errorMessage = data.detail?.[0]?.msg || data.detail || 'Error en la búsqueda';
            throw new Error(errorMessage);
        }
        
        // Guardar los datos actuales
        currentSearchData = data.data || data;
        
        // Mostrar los resultados en la tabla
        showResults(currentSearchData);
        showNotification('Éxito', 'Búsqueda completada correctamente', 'success');
    } catch (error) {
        console.error('Error en la búsqueda:', error);
        showNotification('Error', error.message || 'Error al realizar la búsqueda', 'danger');
    }
}

function validateForm() {
    const startDate = new Date(startDateInput.value);
    const endDate = new Date(endDateInput.value);

    if (startDate > endDate) {
        showNotification('Error', 'La fecha de inicio debe ser anterior a la fecha de fin', 'danger');
        return false;
    }

    return true;
}

function getFormData() {
    const formData = {
        start_date: startDateInput.value,
        end_date: endDateInput.value,
        search_term: searchTermInput.value || null,
        keywords: keywordsInput.value ? keywordsInput.value.split(',').map(k => k.trim()) : [],
        severity: severitySelect.value || null,
        output_format: 'json',
        pretty_json: true,
        custom_delimiter: ','
    };
    
    console.log('Datos del formulario procesados:', formData);
    return formData;
}

function showResults(data) {
    searchResults.classList.remove('d-none');
    resultsTableBody.innerHTML = '';
    
    if (!data || data.length === 0) {
        resultsTableBody.innerHTML = `
            <tr>
                <td colspan="5" class="text-center">No se encontraron resultados</td>
            </tr>
        `;
        return;
    }

    data.forEach(item => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${item.cve_id || item.id || '-'}</td>
            <td>${item.description || item.descriptions?.[0]?.value || '-'}</td>
            <td>
                <span class="badge bg-${getSeverityColor(item.severity || item.metrics?.cvssMetricV31?.[0]?.cvssData?.baseScore || 0)}">
                    ${item.severity || getSeverityLevel(item.metrics?.cvssMetricV31?.[0]?.cvssData?.baseScore || 0)}
                </span>
            </td>
            <td>${formatDate(item.published || item.publishedDate)}</td>
            <td>
                <button class="btn btn-sm btn-outline-primary" onclick="showDetails('${item.cve_id || item.id}')">
                    <i class="bi bi-info-circle"></i> Detalles
                </button>
            </td>
        `;
        resultsTableBody.appendChild(row);
    });
}

function getSeverityColor(severity) {
    const score = typeof severity === 'number' ? severity : 0;
    if (score >= 9.0) return 'danger';
    if (score >= 7.0) return 'warning';
    if (score >= 4.0) return 'info';
    return 'success';
}

function getSeverityLevel(score) {
    if (score >= 9.0) return 'Crítica';
    if (score >= 7.0) return 'Alta';
    if (score >= 4.0) return 'Media';
    return 'Baja';
}

function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

async function downloadData(format) {
    if (!currentSearchData) {
        showNotification('Error', 'No hay datos para descargar', 'danger');
        return;
    }

    try {
        const response = await fetch('/api/convert', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                ...getFormData(),
                output_format: format,
                pretty_json: format === 'json'
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Error en la conversión');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `nist_data_${new Date().toISOString()}.${format}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        showNotification('Éxito', `Archivo ${format.toUpperCase()} descargado correctamente`, 'success');
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error', error.message, 'danger');
    }
}

function showDetails(id) {
    // TODO: Implementar vista detallada de la vulnerabilidad
    showNotification('Info', `Detalles de la vulnerabilidad ${id}`, 'info');
}

function showNotification(title, message, type = 'info') {
    toastTitle.textContent = title;
    toastMessage.textContent = message;
    toastMessage.className = `toast-body text-${type}`;
    notificationToast.show();
} 