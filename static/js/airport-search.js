// TODO: Fix city names with special characters breaking the input field
// TODO: Add correct city names in the suggestions
class AirportAutocomplete {
  constructor(inputId, suggestionsId) {
    this.input = document.getElementById(inputId);
    this.suggestionsContainer = document.getElementById(suggestionsId);
    this.selectedAirportCode = "";
    this.debounceTimer = null;
    this.isLoading = false;

    this.init();
  }

  init() {
    // Event listeners
    this.input.addEventListener("input", (e) => {
      clearTimeout(this.debounceTimer);
      this.debounceTimer = setTimeout(() => {
        this.handleInput(e.target.value);
      }, 300);
    });

    this.input.addEventListener("blur", () => {
      // Delay hiding suggestions to allow click events
      setTimeout(() => {
        this.hideSuggestions();
      }, 200);
    });

    this.input.addEventListener("focus", () => {
      if (this.input.value.length >= 2 && !this.selectedAirportCode) {
        this.handleInput(this.input.value);
      }
    });

    // Hide suggestions when clicking outside
    document.addEventListener("click", (e) => {
      if (
        !this.input.contains(e.target) &&
        !this.suggestionsContainer.contains(e.target)
      ) {
        this.hideSuggestions();
      }
    });

    // Handle keyboard navigation
    this.input.addEventListener("keydown", (e) => {
      this.handleKeyNavigation(e);
    });
  }

  async handleInput(query) {
    console.log(`🔍 handleInput wywołane z query: "${query}"`);

    if (query.length < 2) {
      console.log("❌ Query za krótkie, ukrywam sugestie");
      this.hideSuggestions();
      this.selectedAirportCode = "";
      this.input.dataset.selectedCode = "";
      this.updateInputStyle(false);
      return;
    }

    // Don't search if we already have a selected airport with the same query
    if (
      this.selectedAirportCode &&
      this.input.value.includes(this.selectedAirportCode)
    ) {
      console.log("⏭️ Już mam wybrane lotnisko, pomijam wyszukiwanie");
      return;
    }

    this.isLoading = true;
    this.showLoadingState();

    try {
      const url = `/api/airports?q=${encodeURIComponent(query)}`;
      console.log(`📡 Wysyłam request do: ${url}`);

      const response = await fetch(url);
      console.log(`📨 Otrzymałem odpowiedź:`, response);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const airports = await response.json();
      console.log(`✈️ Otrzymane lotniska:`, airports);
      console.log(`📊 Liczba lotnisk: ${airports.length}`);

      this.showSuggestions(airports);
    } catch (error) {
      console.error("❌ Błąd podczas pobierania lotnisk:", error);
      this.showErrorState();
    } finally {
      this.isLoading = false;
    }
  }

  showLoadingState() {
    this.suggestionsContainer.innerHTML =
      '<div class="loading">Wyszukiwanie lotnisk...</div>';
    this.suggestionsContainer.style.display = "block";
  }

  showErrorState() {
    this.suggestionsContainer.innerHTML =
      '<div class="error">Błąd podczas wyszukiwania lotnisk</div>';
    this.suggestionsContainer.style.display = "block";
    setTimeout(() => {
      this.hideSuggestions();
    }, 3000);
  }

  showSuggestions(airports) {
    console.log(`📋 showSuggestions wywołane z ${airports.length} lotniskami`);

    if (airports.length === 0) {
      console.log("📭 Brak wyników, pokazuję komunikat");
      this.suggestionsContainer.innerHTML =
        '<div class="loading">Brak wyników</div>';
      this.suggestionsContainer.style.display = "block";
      setTimeout(() => {
        this.hideSuggestions();
      }, 2000);
      return;
    }

    console.log("🏗️ Tworzę HTML dla sugestii");
    const html = airports
      .map((airport, index) => {
        console.log(
          `  - ${airport.code}: ${airport.city} (${airport.country})`,
        );
        return `
              <div class="airport-suggestion"
                   data-code="${airport.code}"
                   data-index="${index}"
                   tabindex="0">
                  <div class="airport-code">${airport.code}</div>
                  <div class="airport-name">${this.escapeHtml(airport.name)}</div>
                  <div class="airport-location">${this.escapeHtml(airport.city)}, ${this.escapeHtml(airport.country)}</div>
              </div>
          `;
      })
      .join("");

    console.log("📝 Ustawiam HTML i pokazuję sugestie");
    this.suggestionsContainer.innerHTML = html;
    this.suggestionsContainer.style.display = "block";

    // Add click listeners to suggestions
    this.suggestionsContainer
      .querySelectorAll(".airport-suggestion")
      .forEach((suggestion) => {
        suggestion.addEventListener("click", () => {
          console.log(`🎯 Kliknięto na lotnisko: ${suggestion.dataset.code}`);
          this.selectAirport(suggestion);
        });
      });
  }

  hideSuggestions() {
    this.suggestionsContainer.style.display = "none";
  }

  selectAirport(suggestion) {
    const code = suggestion.dataset.code;
    const cityText = suggestion.querySelector(".airport-location").textContent;
    const city = cityText.split(",")[0];
    this.input.value = `${city} (${code})`;
    this.selectedAirportCode = code;
    this.hideSuggestions();

    // Store selected airport code for form submission
    this.input.dataset.selectedCode = code;
    this.updateInputStyle(true);

    // Trigger change event
    this.input.dispatchEvent(new Event("change"));
  }

  handleKeyNavigation(e) {
    const suggestions = this.suggestionsContainer.querySelectorAll(
      ".airport-suggestion",
    );
    if (suggestions.length === 0) return;

    const currentIndex = Array.from(suggestions).findIndex((s) =>
      s.classList.contains("highlighted"),
    );

    switch (e.key) {
      case "ArrowDown":
        e.preventDefault();
        this.highlightSuggestion(
          suggestions,
          currentIndex < suggestions.length - 1 ? currentIndex + 1 : 0,
        );
        break;
      case "ArrowUp":
        e.preventDefault();
        this.highlightSuggestion(
          suggestions,
          currentIndex > 0 ? currentIndex - 1 : suggestions.length - 1,
        );
        break;
      case "Enter":
        e.preventDefault();
        if (currentIndex >= 0) {
          this.selectAirport(suggestions[currentIndex]);
        }
        break;
      case "Escape":
        this.hideSuggestions();
        break;
    }
  }

  highlightSuggestion(suggestions, index) {
    suggestions.forEach((s) => s.classList.remove("highlighted"));
    if (suggestions[index]) {
      suggestions[index].classList.add("highlighted");
      suggestions[index].scrollIntoView({ block: "nearest" });
    }
  }

  updateInputStyle(isValid) {
    if (isValid) {
      this.input.style.borderColor = "#27ae60";
      this.input.style.backgroundColor = "#f0fff4";
    } else {
      this.input.style.borderColor = "#e1e5e9";
      this.input.style.backgroundColor = "#fff";
    }
  }

  escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  reset() {
    this.selectedAirportCode = "";
    this.input.dataset.selectedCode = "";
    this.updateInputStyle(false);
    this.hideSuggestions();
  }
}

// Form handling
class FlightSearchForm {
  constructor() {
    this.form = document.getElementById("flightForm");
    this.submitBtn = document.getElementById("submit-btn");
    this.departureAutocomplete = null;
    this.arrivalAutocomplete = null;

    this.init();
  }

  init() {
    // Initialize autocomplete
    this.departureAutocomplete = new AirportAutocomplete(
      "departure_airport",
      "departure-suggestions",
    );
    this.arrivalAutocomplete = new AirportAutocomplete(
      "arrival_airport",
      "arrival-suggestions",
    );

    // Form submission handler
    this.form.addEventListener("submit", (e) => {
      this.handleSubmit(e);
    });

    // Notification checkboxes
    this.setupNotificationHandlers();

    // Date validation
    this.setupDateValidation();
  }

  handleSubmit(e) {
    const departureInput = document.getElementById("departure_airport");
    const arrivalInput = document.getElementById("arrival_airport");

    // Validate airport selection
    if (!departureInput.dataset.selectedCode) {
      e.preventDefault();
      this.showError("Proszę wybrać lotnisko wylotu z listy podpowiedzi");
      departureInput.focus();
      return false;
    }

    if (!arrivalInput.dataset.selectedCode) {
      e.preventDefault();
      this.showError("Proszę wybrać lotnisko przylotu z listy podpowiedzi");
      arrivalInput.focus();
      return false;
    }


    // Set airport codes for submission
    departureInput.value = departureInput.dataset.selectedCode;
    arrivalInput.value = arrivalInput.dataset.selectedCode;

    // Show loading state
    this.submitBtn.disabled = true;
    this.submitBtn.textContent = "🔍 Wyszukiwanie...";

    return true;
  }

  setupNotificationHandlers() {
    const emailInput = document.getElementById("email_input");
  }

  setupDateValidation() {
    const today = new Date().toISOString().split("T")[0];
    const departureDate = document.getElementById("departure_date");
    const returnDate = document.getElementById("return_date");

    departureDate.min = today;
    returnDate.min = today;

    departureDate.addEventListener("change", function () {
      returnDate.min = this.value;
      if (returnDate.value && returnDate.value < this.value) {
        returnDate.value = this.value;
      }
    });
  }

  showError(message) {
    // Remove existing error messages
    const existingErrors = document.querySelectorAll(".error.temp-error");
    existingErrors.forEach((error) => error.remove());

    // Create new error message
    const errorDiv = document.createElement("div");
    errorDiv.className = "error temp-error";
    errorDiv.textContent = message;

    // Insert before form
    this.form.parentNode.insertBefore(errorDiv, this.form);

    // Auto-remove after 5 seconds
    setTimeout(() => {
      errorDiv.remove();
    }, 5000);
  }
}

// Initialize when DOM is loaded
document.addEventListener("DOMContentLoaded", function () {
  new FlightSearchForm();
});
