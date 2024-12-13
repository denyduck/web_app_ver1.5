/*
OBSAH
    1. Konstanty a globální proměnné
        1.1 CONSTANTY
        - Odkazuje na HTML elementy, které budou použity pro vyhledávání a zobrazení návrhů.
        - Inicializace instancí Bootstrap modalů pro zobrazení výsledků a PDF souborů.
        1.2 PROMĚNNÉ
        - Drží aktuální indexy zaměřených položek v seznamech, což je použito pro klávesovou navigaci mezi návrhy.

    2. Funkce spojené s inicializací stránky a prvků
        - Kontrola dostupnosti prvků na stránce.
        - Inicializace potřebných funkcí po načtení stránky, např. umístění kurzoru do vyhledávacího pole.
        - Připojení posluchačů událostí pro interakci uživatele.

    3. Seskupení funkcí pro manipulaci s DOM
        - Funkce pro vyčištění návrhů, zobrazení chybových zpráv nebo interakci s uživatelským vstupem.

    4. Komunikace se serverem
        - Volání endpointu "/autocomplete" pro zpracování vyhledávacího dotazu a získání návrhů.

    5. Zobrazení návrhu výsledků uživateli
        - Vyprázdnění seznamu návrhů před přidáním nových výsledků.
        - Vytváření položek návrhu a jejich přidání do seznamu s událostí pro otevření PDF.

    6. Klávesová navigace pro pohyb v modalech
        - Funkce pro interaktivní pohyb v seznamu návrhů a seznamu výsledků pomocí kláves.
        - Zajištění zvýraznění aktivní položky a umožnění rychlého výběru pomocí kláves.

==========================================================================================
==========================================================================================
*/
// 1. Konstanty a globalni promene

// 1.1 CONSTANTY
// prirazeni prvku z DOM
const searchField = document.getElementById('searchField');
const suggestions = document.getElementById('suggestions');
const resultsModal = new bootstrap.Modal(document.getElementById('resultsModal'));
const pdfModal = new bootstrap.Modal(document.getElementById('pdfModal'));
const pdfIframe = document.getElementById('pdfIframe');
const searchButton = document.getElementById('searchButton');

// Globální stav pro focus
const focusState = {
    suggestionFocus: -1,
    resultListFocus: -1,
};

//==========================================================================================
// 2.1 Funkce pro kontrolu dostupnosti prvku DOM
function validateDOMElements() {
    if (!searchField) console.warn("Element #searchField nebyl nalezen.");
    if (!suggestions) console.warn("Element #suggestions nebyl nalezen.");
    if (!resultsModal) console.warn("Modal #resultsModal nebyl inicializován.");
    if (!pdfModal) console.warn("Modal #pdfModal nebyl inicializován.");
    if (!pdfIframe) console.warn("Element #pdfIframe nebyl nalezen.");
}

// Inicializace stránky
function initPage() {
    validateDOMElements();
    attachEventListeners();

    searchField.focus(); // Zaměření na vyhledávací pole
}

window.addEventListener('load', initPage);

//==========================================================================================
// Pomocné funkce a funkce pro přetěžování

// Univerzální funkce pro komunikaci se serverem
function fetchData(endpoint, query) {
    return fetch(`${endpoint}?query=${encodeURIComponent(query)}`)
        .then(response => response.ok ? response.json() : Promise.reject('Chyba: ' + response.statusText));
}

// Univerzální funkce pro fokusování aktuální položky
function setActive(items, focusIndex) {
    Array.from(items).forEach(item => item.classList.remove('active'));
    if (items[focusIndex]) {
        items[focusIndex].classList.add('active');
        items[focusIndex].scrollIntoView({ block: 'nearest' });
    }
}

// Vyčistí kontejner
function clearSuggestions() {
    console.log("cisteni")
    suggestions.innerHTML = ' ';
    suggestions.style.display = 'none';
    focusState.suggestionFocus = -1; // Reset fokusového stavu
}

// Zobrazí chybovou zprávu
function showErrorInSuggestions(message) {
    suggestions.innerHTML = `<li class="list-group-item text-danger">${message}</li>`;
    suggestions.style.display = 'block';
}

// 4. Zpracování návrhů výsledků z /autocomplete
function handleSearchInput() {
    const query = searchField.value.trim();
    if (query.length > 0) {
        const endpoint = '/autocomplete'; // Endpoint pro autocomplete
        fetchData(endpoint, query)
            .then(data => populateSuggestions(data))
            .catch(() => showErrorInSuggestions('Došlo k chybě při načítání návrhů.'));
    } else {
        clearSuggestions();
    }
}

// ==========================================================
// ============ PRÁCE S NÁSEPTÁVÁČEM ========================

// Vysledky pro náseptávač
function populateSuggestions(data) {
    clearSuggestions();                                 //vycisti prechozi navrhy
    if (Array.isArray(data) && data.length > 0) {   //zkontroluje zda jsou data a obsahuji nejake polozky
        data.forEach(item => {                      //pokud jsou data pokracuj
            const suggestionItem = document.createElement('a'); // pro kazdy prvek v poli data se vytvori novy element <a>, ktery reprezentuje navrh
            suggestionItem.className = 'list-group-item list-group-item-action';    //Ziska tricdu pro ostlovani
            suggestionItem.textContent = item.filename;     //nastavi textovy obsah ktery se ma zobrazit
            suggestionItem.dataset.directory = item.directory; // ulozi se do datoveho atributu dataset.directory
            suggestions.appendChild(suggestionItem);

            //pridani posluchace kliknuti pro otevreni PDF Modalu
            suggestionItem.addEventListener('click', () => handleSuggestionsClick(item));  //kazd ynavrh dostane posluchace kliknuti, kdyz se klikne na navrh zavolase fce handle...

            suggestions.appendChild(suggestionItem);
        });
        suggestions.style.display = 'block';  //po pridani vsech navrhu se nastavi styl zobrazi pro kontejner navrhu
    } else {
        showErrorInSuggestions("Nebyly nalezeny žádné návrhy.");
    }
}

// funkce pro zoracovani kliknuti na polozku
function handleSuggestionsClick(item) {
    console.log(item); // Zobrazí objekt item v konzoli, abyste viděli, co obsahuje.

    //otevri pdfmodal
    pdfModal.show();
    // po zobrazeni modalu napln
    pdfModal._element.addEventListener('shown.bs.modal', function() {
        pdfIframe.src = `${item.directory}/${item.filename}`;
    });
    // vycisti vse
    clearSuggestions();
}


// 6. Klávesová navigace ve výsledcích pro náseptávač
function handleKeyboardNavigation(e) {
    const items = suggestions.getElementsByTagName('a'); // Získá seznam návrhů
    if (items.length === 0) return; // Pokud návrhy nejsou, ukončí funkci

    if (e.key === 'ArrowDown') {
        focusState.suggestionFocus = (focusState.suggestionFocus + 1) % items.length; // Posun o 1 dolů
        setActive(items, focusState.suggestionFocus); // Zvýraznění aktivní položky
    } else if (e.key === 'ArrowUp') {
        focusState.suggestionFocus = (focusState.suggestionFocus - 1 + items.length) % items.length; // Posun o 1 nahoru
        setActive(items, focusState.suggestionFocus); // Zvýraznění aktivní položky
    } else if (e.key === 'Enter') {
        e.preventDefault();

        // Pokud je aktivní položka
        if (focusState.suggestionFocus >= 0 && items[focusState.suggestionFocus]) {
            const selectedItem = items[focusState.suggestionFocus];
            pdfModal.show();
            pdfIframe.src = `${selectedItem.dataset.directory}/${selectedItem.textContent}`; // Naplní modal
            clearSuggestions();
            return;
        }

        // Pokud není aktivní položka
        const query = searchField.value.trim();
        if (query.length > 0) {
            showResultsModal(query); // Zobrazí modal s výsledky
            clearSuggestions();
        }
    } else if (e.key === 'Escape') {
        clearSuggestions(); // Vymaže návrhy
    }
}

// ==========================================================
// ============ PRÁCE S PDFLIST MODÁLEM =======================

// 7. Zpracování výsledků hledání ze serveru
function showResultsModal(query) {
    if (query.length > 0) {
        const endpoint = '/autocomplete';
        fetchData(endpoint, query)
            .then(data => populateResultsList(data))
            .catch(() => console.error('Chyba při načítání výsledků.'));
        resultsModal.show();
    } else {
        console.warn('Vyhledávací pole je prázdné.');
    }
}

// Naplánování seznamu v PDF list
function populateResultsList(data) {
    const resultsList = document.getElementById('resultsList');
    resultsList.innerHTML = ''; // Vyčistí předchozí výsledky
    if (Array.isArray(data) && data.length > 0) {
        data.forEach(item => {
            const listItem = document.createElement('li');
            listItem.className = 'list-group-item list-group-item-action';
            listItem.textContent = item.title || item.filename;

            listItem.addEventListener('click', () => handleResultClick(item));
            resultsList.appendChild(listItem);
        });
    } else {
        const noResultsItem = document.createElement('li');
        noResultsItem.className = 'list-group-item text-muted';
        noResultsItem.textContent = 'Žádné výsledky nebyly nalezeny.';
        resultsList.appendChild(noResultsItem);
    }
    resultsModal.show();
}


// Funkce pro zpracování kliknutí na položku v seznamu výsledků
function handleResultClick(item) {
    console.log(item)
    // Zavření modalu s výsledky
    resultsModal.hide();

    // Otevření pdf modalu a naplnění iframe s odpovídajícím souborem
    pdfModal.show();

    pdfModal._element.addEventListener('shown.bs.modal', function() {
        pdfIframe.src = `${item.directory}/${item.filename}`;
    });

    clearSuggestions();
}


// 8. Klávesová navigace v seznamu PDF
function handlePdfListNavigation(e) {
    const listItems = document.querySelectorAll('#resultsList li'); // Načtení položek seznamu
    if (listItems.length === 0) return; // Pokud seznam nemá položky, ukonči funkci

    if (e.key === 'ArrowDown') {
        focusState.resultListFocus = (focusState.resultListFocus + 1) % listItems.length;
        setActive(listItems, focusState.resultListFocus); // Nastaví aktivní položku
    } else if (e.key === 'ArrowUp') {
        focusState.resultListFocus = (focusState.resultListFocus - 1 + listItems.length) % listItems.length;
        setActive(listItems, focusState.resultListFocus); // Nastaví aktivní položku
    } else if (e.key === 'Enter') {
        e.preventDefault();
        if (focusState.resultListFocus >= 0 && listItems[focusState.resultListFocus]) {
            const selectedItem = listItems[focusState.resultListFocus]; // Získá aktivní položku

            // Simulace kliknutí na položku (otevře PDF modal automaticky)
            selectedItem.click();

            // Zavře modal s výsledky
            clearSuggestions();
            closeResultsModal();
        }
    } else if (e.key === 'Escape') {
        clearSuggestions();
        closeResultsModal(); // Zavře modal při stisku Escape

    }
}


// Zavření modalu s výsledky
function closeResultsModal() {
    resultsModal.hide(); // Skryje modal s výsledky
    searchField.focus(); // Zaměření zpět na vyhledávací pole
    clearSuggestions();
}

// Zavření PDF modalu
document.getElementById('pdfModal').addEventListener('hidden.bs.modal', () => {
    searchField.focus(); // Zaměření zpět na vyhledávací pole po zavření PDF modalu
    clearSuggestions();
});


// 9. Připojení posluchačů událostí
function attachEventListeners() {
    searchField.addEventListener('input', handleSearchInput);
    searchField.addEventListener('keydown', handleKeyboardNavigation);
    searchButton.addEventListener('click', () => {
        const query = searchField.value.trim();
        if (query.length > 0) showResultsModal(query);
    });

    document.addEventListener('keydown', handlePdfListNavigation);

    // Refocus search field when any modal is hidden
    document.getElementById('resultsModal').addEventListener('hidden.bs.modal', () => {
        searchField.focus();
    });
    document.getElementById('pdfModal').addEventListener('hidden.bs.modal', () => {
        searchField.focus();
    });
}