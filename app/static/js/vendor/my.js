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
        suggestions.innerHTML = '';                                         // Vyčisti předchozí návrhy

        // Zpracování návrhů
        data.forEach(item => {
          const suggestionItem = document.createElement('a');
          suggestionItem.className = 'list-group-item list-group-item-action';
          suggestionItem.textContent = item.filename;                       // Název souboru

          // Přidání události pro kliknutí na návrh
          suggestionItem.addEventListener('click', function() {
            window.open('/pdfs/' + item.filename, '_blank');                // Otevře PDF v novém okně
            document.getElementById('suggestions').innerHTML = '';          // Vyčistí návrhy
            document.getElementById('searchField').value = item.filename;   // Nastaví vybraný název do vyhledávacího pole
            suggestions.style.display = 'none';                             // Skrýt návrhy po výběru
          });

          suggestions.appendChild(suggestionItem);
        });

        // Zobraz návrhy, pokud existují
        suggestions.style.display = data.length ? 'block' : 'none';
      })
      .catch(error => console.error('Chyba při načítání návrhů:', error));
  });

  // Odeslání vyhledávání při kliknutí na tlačítko
  document.getElementById('searchButton').addEventListener('click', function() {
    const query = document.getElementById('searchField').value;
    if (query) {
      // Přejít na stránku s výsledky
      window.location.href = '/?query=' + encodeURIComponent(query);
    }
  });