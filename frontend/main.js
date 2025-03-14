// Global variables
let data = [];
let selectedMovie = {};
let currentFilter = 'all';
const api = 'http://127.0.0.1:8000/movies';


function filterMovies(filter) {
  console.log("Filtering movies:", filter);
  currentFilter = filter;
  refreshMovies();
}

function tryAdd() {
  let msg = document.getElementById('msg');
  if (msg) msg.innerHTML = '';
}

function tryEditMovie(id) {
  console.log("Editing movie:", id);
  const movie = data.find((x) => x.id === id);
  if (!movie) {
    console.error("Movie not found:", id);
    return;
  }

  selectedMovie = movie;

  const titleEditInput = document.getElementById('title-edit');
  const directorEditInput = document.getElementById('director-edit');
  const yearEditInput = document.getElementById('year-edit');
  const watchedEditInput = document.getElementById('watched-edit');
  const movieId = document.getElementById('movie-id');

  if (movieId) movieId.innerText = movie.id;
  if (titleEditInput) titleEditInput.value = movie.title;
  if (directorEditInput) directorEditInput.value = movie.director;
  if (yearEditInput) yearEditInput.value = movie.release_year;
  if (watchedEditInput) watchedEditInput.checked = movie.watched;

  const editMsg = document.getElementById('edit-msg');
  if (editMsg) editMsg.innerHTML = '';
}

function toggleWatched(id) {
  console.log("Toggling watched status for movie:", id);
  fetch(`${api}/${id}/toggle-watched`, {
    method: 'PUT'
  })
    .then(response => {
      if (response.ok) {
        const movie = data.find(x => x.id === id);
        if (movie) {
          movie.watched = !movie.watched;
          refreshMovies();
        }
      } else {
        console.error("Error toggling watched status");
      }
    })
    .catch(error => {
      console.error("Error:", error);
    });
}

function deleteMovie(id) {
  console.log("Deleting movie:", id);
  fetch(`${api}/${id}`, {
    method: 'DELETE'
  })
    .then(response => {
      if (response.ok) {
        data = data.filter((x) => x.id !== id);
        refreshMovies();
      } else {
        console.error("Error deleting movie");
      }
    })
    .catch(error => {
      console.error("Error:", error);
    });
}


document.addEventListener('DOMContentLoaded', function () {
  console.log("DOM fully loaded");

  const titleInput = document.getElementById('title');
  const directorInput = document.getElementById('director');
  const yearInput = document.getElementById('year');
  const watchedInput = document.getElementById('watched');
  const titleEditInput = document.getElementById('title-edit');
  const directorEditInput = document.getElementById('director-edit');
  const yearEditInput = document.getElementById('year-edit');
  const watchedEditInput = document.getElementById('watched-edit');

  console.log("Form elements found:", {
    titleInput: !!titleInput,
    directorInput: !!directorInput,
    yearInput: !!yearInput,
    watchedInput: !!watchedInput,
    formAdd: !!document.getElementById('form-add')
  });


  const formAdd = document.getElementById('form-add');
  if (formAdd) {
    formAdd.addEventListener('submit', (e) => {
      e.preventDefault();
      console.log("Form submitted");

      const msg = document.getElementById('msg');
      //error handling
      if (!titleInput || !titleInput.value) {
        if (msg) msg.innerHTML = 'Movie title cannot be blank';
        return;
      }

      if (!directorInput || !directorInput.value) {
        if (msg) msg.innerHTML = 'Director name cannot be blank';
        return;
      }

      if (!yearInput || !yearInput.value) {
        if (msg) msg.innerHTML = 'Release year cannot be blank';
        return;
      }


      const title = titleInput.value;
      const director = directorInput.value;
      const year = yearInput.value;
      const watched = watchedInput ? watchedInput.checked : false;

      console.log("Adding movie:", title, director, year, watched);

      fetch(api, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          title,
          director,
          release_year: parseInt(year),
          watched
        })
      })
        .then(response => {
          console.log("Response status:", response.status);
          if (response.ok) {
            return response.json();
          }
          throw new Error('Network response was not ok: ' + response.status);
        })
        .then(newMovie => {
          console.log("Movie added successfully:", newMovie);
          data.push(newMovie);
          refreshMovies();
          resetForm();

          // Close modal
          const closeBtn = document.getElementById('add-close');
          if (closeBtn) {
            closeBtn.click();
          } else {
            console.error("Close button not found");
          }
        })
        .catch(error => {
          console.error("Error adding movie:", error);
          if (msg) msg.innerHTML = 'Error adding movie: ' + error.message;
        });
    });
  } else {
    console.error("Form element not found");
  }


  const formEdit = document.getElementById('form-edit');
  if (formEdit) {
    formEdit.addEventListener('submit', (e) => {
      e.preventDefault();
      console.log("Edit form submitted");

      const editMsg = document.getElementById('edit-msg');

      if (!titleEditInput || !titleEditInput.value) {
        if (editMsg) editMsg.innerHTML = 'Movie title cannot be blank';
        return;
      }

      if (!directorEditInput || !directorEditInput.value) {
        if (editMsg) editMsg.innerHTML = 'Director name cannot be blank';
        return;
      }

      if (!yearEditInput || !yearEditInput.value) {
        if (editMsg) editMsg.innerHTML = 'Release year cannot be blank';
        return;
      }

      const title = titleEditInput.value;
      const director = directorEditInput.value;
      const year = yearEditInput.value;
      const watched = watchedEditInput ? watchedEditInput.checked : false;

      console.log("Editing movie:", selectedMovie.id, title, director, year, watched);

      fetch(`${api}/${selectedMovie.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          title,
          director,
          release_year: parseInt(year),
          watched
        })
      })
        .then(response => {
          if (response.ok) {

            selectedMovie.title = title;
            selectedMovie.director = director;
            selectedMovie.release_year = parseInt(year);
            selectedMovie.watched = watched;
            refreshMovies();


            const closeBtn = document.getElementById('edit-close');
            if (closeBtn) {
              closeBtn.click();
            }
          } else {
            console.error("Error updating movie");
            if (editMsg) editMsg.innerHTML = 'Error updating movie';
          }
        })
        .catch(error => {
          console.error("Error:", error);
          if (editMsg) editMsg.innerHTML = 'Error updating movie: ' + error.message;
        });
    });
  }


  getMovies();
});

// helper functions
function refreshMovies() {
  console.log("Refreshing movies with filter:", currentFilter);
  const moviesDiv = document.getElementById('movies');
  if (!moviesDiv) {
    console.error("Movies div not found");
    return;
  }

  moviesDiv.innerHTML = '';
  let filteredData = [...data];

  if (currentFilter === 'watched') {
    filteredData = data.filter(movie => movie.watched);
  } else if (currentFilter === 'unwatched') {
    filteredData = data.filter(movie => !movie.watched);
  }

  console.log("Filtered data:", filteredData);

  filteredData
    .sort((a, b) => b.id - a.id)
    .forEach((movie) => {
      const watchedStatus = movie.watched ? 'Watched' : 'To Watch';
      const statusClass = movie.watched ? 'watched' : 'unwatched';

      const movieCard = document.createElement('div');
      movieCard.className = `movie-card ${statusClass}`;
      movieCard.innerHTML = `
        <div class="movie-header">
          <h4>${movie.title} (${movie.release_year})</h4>
          <span class="badge ${movie.watched ? 'bg-success' : 'bg-warning'}">${watchedStatus}</span>
        </div>
        <p class="text-secondary">Director: ${movie.director}</p>
        <div class="options">
          <i onclick="toggleWatched(${movie.id})" class="fas ${movie.watched ? 'fa-eye-slash' : 'fa-eye'}"></i>
          <i onclick="tryEditMovie(${movie.id})" class="fas fa-edit" data-bs-toggle="modal" data-bs-target="#editModal"></i>
          <i onclick="deleteMovie(${movie.id})" class="fas fa-trash-alt"></i>
        </div>
      `;

      moviesDiv.appendChild(movieCard);
    });
}

function resetForm() {
  const titleInput = document.getElementById('title');
  const directorInput = document.getElementById('director');
  const yearInput = document.getElementById('year');
  const watchedInput = document.getElementById('watched');

  if (titleInput) titleInput.value = '';
  if (directorInput) directorInput.value = '';
  if (yearInput) yearInput.value = '';
  if (watchedInput) watchedInput.checked = false;
}

function getMovies() {
  console.log("Getting movies from API");
  fetch(api)
    .then(response => {
      if (response.ok) {
        return response.json();
      }
      throw new Error('Network response was not ok');
    })
    .then(movies => {
      console.log("Movies retrieved:", movies);
      data = movies || [];
      refreshMovies();
    })
    .catch(error => {
      console.error("Error getting movies:", error);
    });
}