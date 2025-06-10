document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('searchForm');
    const searchButton = document.getElementById('searchButton');
    
    if (searchForm) {
        searchForm.addEventListener('submit', handleFormSubmit);
    }
    
    if (searchButton) {
        searchButton.addEventListener('click', handleFormSubmit);
    }
});

function getFormData() {
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    const searchTerm = document.getElementById('searchTerm').value;
    const keywords = document.getElementById('keywords').value.split(',').map(k => k.trim()).filter(k => k);
    const severity = document.getElementById('severity').value;
    
    // Guardar la severidad seleccionada en sessionStorage
    if (severity) {
        sessionStorage.setItem('selectedSeverity', severity);
    }
    
    return {
        start_date: startDate,
        end_date: endDate,
        search_term: searchTerm,
        keywords: keywords,
        severity: severity || undefined,
        output_format: 'json',
        pretty_json: true
    };
}

async function handleFormSubmit(event) {
    event.preventDefault();
    
    const searchButton = document.getElementById('searchButton');
    if (searchButton) {
        searchButton.disabled = true;
        searchButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Buscando...';
    }
    
    try {
        const formData = getFormData();
        console.log('Enviando datos:', formData);
        
        const response = await fetch('/api/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Error en la búsqueda');
        }
        
        const data = await response.json();
        console.log('Respuesta recibida:', data);
        
        // Guardar los resultados en sessionStorage
        sessionStorage.setItem('searchResults', JSON.stringify(data));
        
        // Redirigir a la página de resultados
        window.location.href = '/results';
        
    } catch (error) {
        console.error('Error:', error);
        showNotification(error.message || 'Error al realizar la búsqueda', 'danger');
    } finally {
        if (searchButton) {
            searchButton.disabled = false;
            searchButton.textContent = 'Buscar';
        }
    }
}

function showNotification(message, type = 'info') {
    const notificationDiv = document.createElement('div');
    notificationDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 end-0 m-3`;
    notificationDiv.style.zIndex = '1050';
    notificationDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    document.body.appendChild(notificationDiv);
    
    setTimeout(() => {
        notificationDiv.remove();
    }, 5000);
} 