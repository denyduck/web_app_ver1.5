/*
Data se budou dynamicky nacitat, proto je na servrove casti vracen
front-endu json, s json nyni muze pracovat AJAX

OBSAH
    1. Zavolej serve, ziskej seznam souboru a dynamicky vykresli akordeon
    2. Vytvor akordeon z nactenych dat a pripoj jej do DOM
    3.Zobraz PDF v modalu
*/
// inicializuje accordionContainer
document.addEventListener('DOMContentLoaded', () => {
    const accordionContainer = document.getElementById('accordionContainer');

    if (!accordionContainer) {
        console.error('Prvek accordionContainer nebyl nalezen v DOM!');
        return; // Ukončí funkci, pokud není element nalezen
    }

    // 1. Vytvoří spinner (označení A)
    const loadingSpinner = document.createElement('div');
    loadingSpinner.classList.add('spinner-border', 'text-primary');
    loadingSpinner.setAttribute('role', 'status');
    loadingSpinner.innerHTML = '<span class="visually-hidden">Načítání...</span>';
    accordionContainer.appendChild(loadingSpinner); // Spinner přidán do DOM

    // Funkce pro načítání souborů s indikátorem
    function loadFiles() {
        fetch('/prohlizet/data')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP chyba: ${response.status}`);
                }
                return response.json();
            })
            .then(files => {
                // 2. Odstraní spinner po úspěšném načtení dat (označení B)
                loadingSpinner.remove();

                if (files.length === 0) {
                    accordionContainer.innerHTML = `
                        <div class="alert alert-info text-center">
                            Dosud nebyly nalezeny žádné soubory.
                        </div>`;
                    return;
                }

                // Vytvoření HTML pro accordion
                let accordionHTML = '';
                files.forEach((file, index) => {
                    const isFirst = index === 0; // První položka otevřená
                    const pdfPath = `/pdfs/${file.directory}/${file.filename}`; // Dynamická cesta k PDF

                    accordionHTML += `
                        <div class="accordion accordion-flush">
                            <div class="accordion-item">
                                <h2 class="accordion-header" id="heading${index}">
                                    <button
                                        class="accordion-button ${isFirst ? '' : 'collapsed'}"
                                        type="button"
                                        data-bs-toggle="collapse"
                                        data-bs-target="#collapse${index}"
                                        aria-expanded="${isFirst}"
                                        aria-controls="collapse${index}">
                                        ${file.filename}
                                    </button>
                                </h2>
                                <div
                                    id="collapse${index}"
                                    class="accordion-collapse collapse ${isFirst ? 'show' : ''}"
                                    aria-labelledby="heading${index}"
                                    data-bs-parent="#accordionContainer">
                                    <div class="accordion-body">
                                        <p class="text-muted mb-3">
                                            ${file.kontent || 'Bez obsahu'}
                                        </p>

                                        <div class="d-flex justify-content-between">
                                            <button class="btn btn-sm btn-primary"
                                                    onclick="openPdfModal('${pdfPath}', '${file.filename}')">
                                                Náhled
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                });

                accordionContainer.innerHTML = accordionHTML; // Vykreslení na stránku
            })
            .catch(error => {
                console.error('Chyba při načítání souborů:', error);
                // 3. Odstraní spinner při chybě (označení C)
                loadingSpinner.remove();
                accordionContainer.innerHTML = `
                    <div class="alert alert-danger text-center">
                        Chyba při načítání dat ze serveru.
                    </div>`;
            });
    }

    // Zavolání funkce pro načtení souborů
    loadFiles();
});

// Funkce pro otevření modálního okna s náhledem PDF
function openPdfModal(pdfPath, filename) {
    // Nastav src pro iframe na cestu k PDF
    const pdfIframe = document.getElementById('pdfIframe');
    if (pdfIframe) {
        pdfIframe.src = pdfPath;
    }

    // Nastav titulek modálního okna na název souboru
    const pdfModalLabel = document.getElementById('pdfModalLabel');
    if (pdfModalLabel) {
        pdfModalLabel.textContent = filename;
    }

    // Najdi modal a otevři ho
    const pdfModal = new bootstrap.Modal(document.getElementById('pdfModal'));
    pdfModal.show();
}