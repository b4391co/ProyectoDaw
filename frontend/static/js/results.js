document.addEventListener('DOMContentLoaded', function() {
    const resultsTable = document.getElementById('resultsTable');
    
    // Obtener los datos de la URL
    const urlParams = new URLSearchParams(window.location.search);
    const dataParam = urlParams.get('data');
    
    if (!dataParam) {
        showError('No se encontraron datos de búsqueda');
        return;
    }

    try {
        const data = JSON.parse(decodeURIComponent(dataParam));
        displayResults(data.vulnerabilities);
    } catch (error) {
        console.error('Error al procesar los datos:', error);
        showError('Error al procesar los resultados');
    }
});

function displayResults(vulnerabilities) {
    const resultsTable = document.getElementById('resultsTable');
    
    if (!vulnerabilities || vulnerabilities.length === 0) {
        showError('No se encontraron vulnerabilidades');
        return;
    }

    // Añadir contador de resultados
    const resultCount = document.createElement('div');
    resultCount.className = 'alert alert-info mb-4';
    resultCount.innerHTML = `Se encontraron <strong>${vulnerabilities.length}</strong> vulnerabilidades`;
    document.querySelector('.card-body').insertBefore(resultCount, document.querySelector('.table-responsive'));

    vulnerabilities.forEach(vuln => {
        const row = document.createElement('tr');
        
        // Extraer la severidad del CVSS
        const cvssV3 = vuln.cve?.metrics?.cvssMetricV31?.[0]?.cvssData;
        const cvssV2 = vuln.cve?.metrics?.cvssMetricV2?.[0];
        const severity = cvssV3?.baseSeverity || cvssV2?.baseSeverity || 'UNKNOWN';
        const score = cvssV3?.baseScore || cvssV2?.baseScore || 'N/A';
        
        // Formatear la fecha
        const publishedDate = new Date(vuln.cve?.published || '').toLocaleDateString();
        
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
            <td>${publishedDate}</td>
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
    
    // Buscar la descripción completa en los datos originales
    const urlParams = new URLSearchParams(window.location.search);
    const dataParam = urlParams.get('data');
    const data = JSON.parse(decodeURIComponent(dataParam));
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