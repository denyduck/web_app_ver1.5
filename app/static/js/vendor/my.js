let currentFocus = -1; // Pro sledování aktuální pozice ve výběru

// Načítání návrhů na základě vstupu uživatele
document.getElementById('searchField').addEventListener('input', function() {
  let query = this.value;

  // Pokud je dotaz prázdný, vyčisti návrhy
  if (!query) {
    document.getElementById('suggestions').innerHTML = '';
    document.getElementById('suggestions').style.display = 'none';
    return;
  }

  // AJAX volání pro získání návrhů
  fetch('/autocomplete?query=' + encodeURIComponent(query))
    .then(response => response.json())
    .then(data => {
      const suggestions = document.getElementById('suggestions');
      suggestions.innerHTML = '';                                  // Vyčisti předchozí návrhy
      currentFocus = -1;                                           // Resetuj aktuální pozici při novém hledání

      // Zpracování návrhů
      data.forEach((item) => {
        const suggestionItem = document.createElement('a');
        suggestionItem.className = 'list-group-item list-group-item-action';
        suggestionItem.textContent = item.filename;               // Název souboru

        // Přidání události pro kliknutí na návrh
        suggestionItem.addEventListener('click', function() {
          window.open('/pdfs/' + item.filename, '_blank');        // Otevře PDF v novém okně
          document.getElementById('suggestions').innerHTML = '';  // Vyčisti návrhy
          document.getElementById('searchField').value = '';      // Vyprázdni vyhledávací pole
          suggestions.style.display = 'none';                      // Skrýt návrhy po výběru
        });

        suggestions.appendChild(suggestionItem);
      });

      // Zobraz návrhy, pokud existují
      suggestions.style.display = data.length ? 'block' : 'none';
    })
    .catch(error => console.error('Chyba při načítání návrhů:', error));
});

// Navigace v návrzích pomocí klávesnice
document.getElementById('searchField').addEventListener('keydown', function(e) {
  const suggestions = document.getElementById('suggestions');
  const items = suggestions.getElementsByTagName('a');

  if (e.key === 'ArrowDown') {
    // Šipka dolů
    currentFocus++;
    if (currentFocus >= items.length) currentFocus = 0;
    setActive(items);
  } else if (e.key === 'ArrowUp') {
    // Šipka nahoru
    currentFocus--;
    if (currentFocus < 0) currentFocus = items.length - 1;
    setActive(items);
  } else if (e.key === 'Enter') {
    // Potvrzení klávesou Enter
    e.preventDefault();

    // Pokud je v našeptávači vybrána nějaká položka, vyber ji
    if (currentFocus > -1 && items[currentFocus]) {
      items[currentFocus].click();
    } else {
      // Pokud není vybrán žádný návrh, spustí se vyhledávání stejně jako při kliknutí na tlačítko "Hledat"
      searchFiles();
    }
  } else if (e.key === 'Escape') {
    // Zavření návrhů klávesou Escape
    suggestions.style.display = 'none';
  }
});

// Přidání události, která skryje našeptávač při kliknutí mimo něj
document.addEventListener('click', function(event) {
  const searchField = document.getElementById('searchField');
  const suggestions = document.getElementById('suggestions');

  // Zkontroluj, zda bylo kliknuto mimo vyhledávací pole nebo našeptávač
  if (!searchField.contains(event.target) && !suggestions.contains(event.target)) {
    suggestions.style.display = 'none';  // Stejně jako při stisku klávesy Escape
  }
});

// Nastaví aktivní prvek v seznamu návrhů
function setActive(items) {
  // Odstraní aktivní třídu ze všech položek
  for (let i = 0; i < items.length; i++) {
    items[i].classList.remove('active');
  }
  // Přidá aktivní třídu k aktuální položce
  if (items[currentFocus]) {
    items[currentFocus].classList.add('active');
    items[currentFocus].scrollIntoView({ block: "nearest" });
  }
}

// Funkce pro spuštění vyhledávání (použitá jak pro tlačítko, tak pro klávesu Enter)
function searchFiles() {
  let query = document.getElementById('searchField').value;

  // Pokud je dotaz prázdný, vyčisti návrhy a modální okno
  if (!query) {
    document.getElementById('resultsList').innerHTML = '<li class="list-group-item">Zadejte hledaný název.</li>';
    const resultsModal = new bootstrap.Modal(document.getElementById('resultsModal'));
    resultsModal.show();
    return;
  }

  // AJAX volání pro získání výsledků
  fetch('/autocomplete?query=' + encodeURIComponent(query))
    .then(response => response.json())
    .then(data => {
      const resultsList = document.getElementById('resultsList');
      resultsList.innerHTML = '';               // Vyčisti předchozí výsledky

      if (data.length > 0) {
        // Pro každý nalezený soubor přidáme do seznamu novou položku
        data.forEach((item) => {
          const resultItem = document.createElement('li');
          resultItem.className = 'list-group-item';

          // Odkaz na PDF soubor
          const link = document.createElement('a');
          link.href = '/pdfs/' + item.filename;
          link.target = '_blank';               // Otevře PDF v novém okně
          link.textContent = item.filename;     // Zobrazí název souboru

          resultItem.appendChild(link);
          resultsList.appendChild(resultItem);
        });
      } else {
        // Pokud nejsou nalezeny žádné výsledky
        resultsList.innerHTML = '<li class="list-group-item">Žádné výsledky nenalezeny.</li>';
      }

      // Zobrazení modálního okna s výsledky
      const resultsModal = new bootstrap.Modal(document.getElementById('resultsModal'));
      resultsModal.show();

      // Vyprázdni vyhledávací pole po zobrazení výsledků
      document.getElementById('searchField').value = '';
    })
    .catch(error => {
      console.error('Chyba při vyhledávání:', error);
      document.getElementById('resultsList').innerHTML = '<li class="list-group-item">Došlo k chybě při vyhledávání.</li>';
      const resultsModal = new bootstrap.Modal(document.getElementById('resultsModal'));
      resultsModal.show();

      // Vyprázdni vyhledávací pole i v případě chyby
      document.getElementById('searchField').value = '';
    });
}

// Vyhledávání po kliknutí na tlačítko "Hledat"
document.getElementById('searchButton').addEventListener('click', function() {
  searchFiles();
});

// Umístění kurzoru do vyhledávacího pole při načtení stránky
window.addEventListener('load', function() {
  // Vyprázdnění vyhledávacího pole a odstranění posledního hledání
  localStorage.removeItem('lastSearch'); // Odstranění posledního hledání
  document.getElementById('searchField').value = ''; // Vyprázdní vyhledávací pole
  document.getElementById('searchField').focus(); // Umístí kurzor do vyhledávacího pole
});

// Přidání události pro zavření modálu
document.getElementById('resultsModal').addEventListener('hidden.bs.modal', function() {
  // Vyprázdni a skryj našeptávač při zavření modálního okna
  document.getElementById('suggestions').innerHTML = '';
  document.getElementById('suggestions').style.display = 'none';
  document.getElementById('searchField').focus();
});