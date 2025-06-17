// Variable global para almacenar los datos
let currentVulnerabilities = [];

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM Content Loaded');
    const resultsTable = document.getElementById('resultsTable');
    const downloadCsvBtn = document.getElementById('downloadCsvBtn');
    const downloadJsonBtn = document.getElementById('downloadJsonBtn');
    
    console.log('Buttons found:', {
        csv: downloadCsvBtn,
        json: downloadJsonBtn
    });
    
    // Obtener los datos del sessionStorage
    const storedData = sessionStorage.getItem('searchResults');
    console.log('Stored data:', storedData ? 'exists' : 'not found');
    
    if (!storedData) {
        showError('No se encontraron datos de búsqueda');
        return;
    }

    try {
        const data = JSON.parse(storedData);
        console.log('Parsed data:', data);
        // Guardar los datos en la variable global
        currentVulnerabilities = data.vulnerabilities;
        
        // Obtener la severidad seleccionada del sessionStorage
        const selectedSeverity = sessionStorage.getItem('selectedSeverity');
        displayResults(currentVulnerabilities, selectedSeverity);
        
        // Configurar los botones de descarga directamente
        downloadCsvBtn.onclick = function() {
            const csvContent = convertToCSV(currentVulnerabilities);
            downloadFile(csvContent, 'csv');
        };
        
        downloadJsonBtn.onclick = function() {
            const jsonContent = JSON.stringify(currentVulnerabilities, null, 2);
            downloadFile(jsonContent, 'json');
        };
        
        // Limpiar sessionStorage
        sessionStorage.removeItem('searchResults');
        sessionStorage.removeItem('selectedSeverity');
    } catch (error) {
        console.error('Error:', error);
        showError('Error al procesar los resultados');
    }
});

function downloadFile(content, format) {
    const blob = new Blob([content], { 
        type: format === 'csv' ? 'text/csv;charset=utf-8;' : 'application/json;charset=utf-8;'
    });
    
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    link.setAttribute('href', url);
    link.setAttribute('download', `nist_vulnerabilities.${format}`);
    link.style.visibility = 'hidden';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

function convertToCSV(vulnerabilities) {
    console.log('Converting to CSV');
    // Definir las columnas que queremos en el CSV
    const headers = ['CVE ID', 'Descripción', 'Severidad', 'Score', 'Fecha Publicación', 'Fecha Modificación'];
    
    // Crear las filas del CSV
    const rows = vulnerabilities.map(vuln => {
        const cvssV3 = vuln.cve?.metrics?.cvssMetricV31?.[0]?.cvssData;
        const cvssV2 = vuln.cve?.metrics?.cvssMetricV2?.[0];
        const severity = cvssV3?.baseSeverity || cvssV2?.baseSeverity || 'UNKNOWN';
        const score = cvssV3?.baseScore || cvssV2?.baseScore || 'N/A';
        const description = vuln.cve?.descriptions?.[0]?.value || 'No description available';
        const publishedDate = new Date(vuln.cve?.published || '').toLocaleDateString();
        const lastModifiedDate = new Date(vuln.cve?.lastModified || '').toLocaleDateString();

        return [
            vuln.cve?.id || 'N/A',
            `"${description.replace(/"/g, '""')}"`, // Escapar comillas en la descripción
            severity,
            score,
            publishedDate,
            lastModifiedDate
        ];
    });

    // Combinar headers y rows
    return [headers, ...rows].map(row => row.join(',')).join('\n');
}

function displayResults(vulnerabilities, selectedSeverity) {
    const resultsTable = document.getElementById('resultsTable');
    
    if (!vulnerabilities || vulnerabilities.length === 0) {
        showError('No se encontraron vulnerabilidades');
        return;
    }

    // Filtrar vulnerabilidades por severidad si se especificó
    let filteredVulnerabilities = vulnerabilities;
    if (selectedSeverity) {
        filteredVulnerabilities = vulnerabilities.filter(vuln => {
            const cvssV3 = vuln.cve?.metrics?.cvssMetricV31?.[0]?.cvssData;
            return cvssV3?.baseSeverity === selectedSeverity;
        });
    }

    if (filteredVulnerabilities.length === 0) {
        showError(`No se encontraron vulnerabilidades con severidad ${selectedSeverity || 'seleccionada'}`);
        return;
    }

    // Añadir contador de resultados
    const resultCount = document.createElement('div');
    resultCount.className = 'alert alert-info mb-4';
    resultCount.innerHTML = `Se encontraron <strong>${filteredVulnerabilities.length}</strong> vulnerabilidades${selectedSeverity ? ` con severidad ${selectedSeverity}` : ''}`;
    document.querySelector('.card-body').insertBefore(resultCount, document.querySelector('.table-responsive'));

    filteredVulnerabilities.forEach(vuln => {
        const row = document.createElement('tr');
        
        // Extraer la severidad del CVSS
        const cvssV3 = vuln.cve?.metrics?.cvssMetricV31?.[0]?.cvssData;
        const cvssV2 = vuln.cve?.metrics?.cvssMetricV2?.[0];
        const severity = cvssV3?.baseSeverity || cvssV2?.baseSeverity || 'UNKNOWN';
        const score = cvssV3?.baseScore || cvssV2?.baseScore || 'N/A';
        
        // Formatear las fechas
        const publishedDate = new Date(vuln.cve?.published || '').toLocaleDateString();
        const lastModifiedDate = new Date(vuln.cve?.lastModified || '').toLocaleDateString();
        
        // Obtener la descripción
        const description = vuln.cve?.descriptions?.[0]?.value || 'No description available';
        const shortDescription = description.length > 100 ? 
            description.substring(0, 100) + '...' : 
            description;
        
        row.innerHTML = `
            <td>
                <a href="https://nvd.nist.gov/vuln/detail/${vuln.cve?.id}" 
                   target="_blank" 
                   class="text-decoration-none fw-bold">
                    ${vuln.cve?.id || 'N/A'}
                </a>
            </td>
            <td>
                <div class="description-cell">
                    ${shortDescription}
                    ${description.length > 100 ? 
                        `<button class="btn btn-link btn-sm p-0 ms-2" 
                                onclick="showFullDescription(this, '${vuln.cve?.id}')">
                            Ver más
                        </button>` : 
                        ''}
                </div>
            </td>
            <td>
                <div class="d-flex align-items-center">
                    <span class="severity-${severity} me-2">${severity}</span>
                    <span class="badge bg-secondary">${score}</span>
                </div>
            </td>
            <td>
                <a href="https://nvd.nist.gov/vuln/detail/${vuln.cve?.id}" 
                   target="_blank" 
                   class="text-decoration-none">
                    ${vuln.cve?.id || 'N/A'}
                </a>
            </td>
            <td>
                <div class="d-flex flex-column">
                    <small class="text-muted">Publicación:</small>
                    <span>${publishedDate}</span>
                    <small class="text-muted mt-1">Última modificación:</small>
                    <span>${lastModifiedDate}</span>
                </div>
            </td>
            <td>
                <div class="btn-group">
                    <button class="btn btn-sm btn-outline-primary" 
                            onclick="showDetails('${vuln.cve?.id}')">
                        Detalles
                    </button>
                    <button class="btn btn-sm btn-outline-secondary" 
                            onclick="copyCveId('${vuln.cve?.id}')">
                        Copiar ID
                    </button>
                </div>
            </td>
        `;
        
        resultsTable.appendChild(row);
    });
}

function showError(message) {
    const container = document.querySelector('.container');
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-danger alert-dismissible fade show';
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    container.insertBefore(alertDiv, container.firstChild);
}

function showDetails(cveId) {
    window.open(`https://nvd.nist.gov/vuln/detail/${cveId}`, '_blank');
}

function copyCveId(cveId) {
    navigator.clipboard.writeText(cveId).then(() => {
        const button = event.target;
        const originalText = button.textContent;
        button.textContent = '¡Copiado!';
        setTimeout(() => {
            button.textContent = originalText;
        }, 2000);
    });
}

function showFullDescription(button, cveId) {
    const descriptionCell = button.closest('.description-cell');
    const shortDescription = descriptionCell.textContent.replace('Ver más', '').trim();
    
    // Buscar la descripción completa en los datos almacenados
    const storedData = sessionStorage.getItem('searchResults');
    if (storedData) {
        const data = JSON.parse(storedData);
        const vuln = data.vulnerabilities.find(v => v.cve?.id === cveId);
        
        if (vuln) {
            const fullDescription = vuln.cve?.descriptions?.[0]?.value || shortDescription;
            descriptionCell.innerHTML = `
                ${fullDescription}
                <button class="btn btn-link btn-sm p-0 ms-2" 
                        onclick="showShortDescription(this, '${shortDescription}')">
                    Ver menos
                </button>
            `;
        }
    }
}

function showShortDescription(button, shortDescription) {
    const descriptionCell = button.closest('.description-cell');
    descriptionCell.innerHTML = `
        ${shortDescription}
        <button class="btn btn-link btn-sm p-0 ms-2" 
                onclick="showFullDescription(this, '${descriptionCell.closest('tr').querySelector('a').textContent.trim()}')">
            Ver más
        </button>
    `;
} 