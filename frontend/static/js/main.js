document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('searchForm');
    const startDateInput = document.getElementById('startDate');
    const endDateInput = document.getElementById('endDate');

    // Establecer fechas por defecto (últimos 4 días)
    const today = new Date();
    const fourDaysAgo = new Date(today);
    fourDaysAgo.setDate(today.getDate() - 4);

    startDateInput.value = fourDaysAgo.toISOString().split('T')[0];
    endDateInput.value = today.toISOString().split('T')[0];

    // Función para mostrar notificaciones
    function showNotification(message, type = 'success') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.role = 'alert';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        document.querySelector('.container').insertBefore(alertDiv, document.querySelector('.row'));
        
        // Auto-cerrar después de 5 segundos
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }

    // Función para obtener los datos del formulario
    function getFormData() {
        const keywords = document.getElementById('keywords').value
            .split(',')
            .map(k => k.trim())
            .filter(k => k.length > 0);

        return {
            start_date: startDateInput.value,
            end_date: endDateInput.value,
            severity: document.getElementById('severity').value || null,
            search_term: document.getElementById('searchTerm').value || null,
            keywords: keywords
        };
    }

    // Manejar el envío del formulario
    searchForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
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

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Error en la búsqueda');
            }

            const data = await response.json();
            console.log('Respuesta recibida:', data);

            // Redirigir a la página de resultados con los datos
            window.location.href = `/results?data=${encodeURIComponent(JSON.stringify(data))}`;

        } catch (error) {
            console.error('Error:', error);
            showNotification(error.message, 'danger');
        }
    });
}); 