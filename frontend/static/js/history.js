// Estado de la paginación
let currentPage = 1;
const itemsPerPage = 10;
let currentStatus = null;

// Elementos del DOM
const tableBody = document.getElementById('historyTableBody');
const prevPageBtn = document.getElementById('prevPage');
const nextPageBtn = document.getElementById('nextPage');
const currentPageSpan = document.getElementById('currentPage');
const itemsCountSpan = document.getElementById('itemsCount');
const filterAllBtn = document.getElementById('filterAll');
const filterSuccessBtn = document.getElementById('filterSuccess');
const filterErrorBtn = document.getElementById('filterError');

// Modal elements
const conversionModal = new bootstrap.Modal(document.getElementById('conversionModal'));
const requestDetails = document.getElementById('requestDetails');
const responseDetails = document.getElementById('responseDetails');
const errorDetails = document.getElementById('errorDetails');
const errorContent = document.getElementById('errorContent');

// Cargar el historial inicial
document.addEventListener('DOMContentLoaded', () => {
    loadHistory();
    setupEventListeners();
});

function setupEventListeners() {
    // Event listeners para los botones de paginación
    prevPageBtn.addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            loadHistory();
        }
    });

    nextPageBtn.addEventListener('click', () => {
        currentPage++;
        loadHistory();
    });

    // Event listeners para los filtros
    filterAllBtn.addEventListener('click', () => {
        currentStatus = null;
        currentPage = 1;
        loadHistory();
        updateFilterButtons(filterAllBtn);
    });

    filterSuccessBtn.addEventListener('click', () => {
        currentStatus = 'success';
        currentPage = 1;
        loadHistory();
        updateFilterButtons(filterSuccessBtn);
    });

    filterErrorBtn.addEventListener('click', () => {
        currentStatus = 'error';
        currentPage = 1;
        loadHistory();
        updateFilterButtons(filterErrorBtn);
    });
}

function updateFilterButtons(activeButton) {
    [filterAllBtn, filterSuccessBtn, filterErrorBtn].forEach(btn => {
        btn.classList.remove('active');
    });
    activeButton.classList.add('active');
}

async function loadHistory() {
    try {
        const skip = (currentPage - 1) * itemsPerPage;
        let url = `/api/history?skip=${skip}&limit=${itemsPerPage}`;
        if (currentStatus) {
            url += `&status=${currentStatus}`;
        }

        const response = await fetch(url);
        if (!response.ok) {
            throw new Error('Error al cargar el historial');
        }

        const data = await response.json();
        renderHistory(data);
        updatePagination(data.length);
    } catch (error) {
        console.error('Error:', error);
        showError('Error al cargar el historial');
    }
}

function renderHistory(conversions) {
    tableBody.innerHTML = '';
    
    if (conversions.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td colspan="5" class="text-center py-4">
                No hay conversiones para mostrar
            </td>
        `;
        tableBody.appendChild(row);
        return;
    }

    conversions.forEach(conversion => {
        const row = document.createElement('tr');
        const date = new Date(conversion.created_at).toLocaleString();
        
        row.innerHTML = `
            <td>${conversion.id}</td>
            <td>${date}</td>
            <td>${conversion.request.format.toUpperCase()}</td>
            <td>
                <span class="badge ${conversion.status === 'success' ? 'bg-success' : 'bg-danger'}">
                    ${conversion.status === 'success' ? 'Exitoso' : 'Error'}
                </span>
            </td>
            <td>
                <button class="btn btn-sm btn-outline-primary view-details" data-id="${conversion.id}">
                    <i class="bi bi-eye"></i> Ver detalles
                </button>
            </td>
        `;

        // Event listener para el botón de detalles
        row.querySelector('.view-details').addEventListener('click', () => {
            showConversionDetails(conversion);
        });

        tableBody.appendChild(row);
    });
}

function updatePagination(itemsCount) {
    itemsCountSpan.textContent = itemsCount;
    currentPageSpan.textContent = currentPage;
    
    // Actualizar estado de los botones de paginación
    prevPageBtn.disabled = currentPage === 1;
    nextPageBtn.disabled = itemsCount < itemsPerPage;
}

function showConversionDetails(conversion) {
    // Mostrar detalles de la solicitud
    requestDetails.textContent = JSON.stringify(conversion.request, null, 2);
    
    // Mostrar detalles de la respuesta
    responseDetails.textContent = JSON.stringify(conversion.response, null, 2);
    
    // Mostrar error si existe
    if (conversion.error) {
        errorDetails.classList.remove('d-none');
        errorContent.textContent = JSON.stringify(conversion.error, null, 2);
    } else {
        errorDetails.classList.add('d-none');
    }
    
    // Mostrar el modal
    conversionModal.show();
}

function showError(message) {
    // Implementar un sistema de notificaciones si es necesario
    alert(message);
} 