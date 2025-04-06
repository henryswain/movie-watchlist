<script setup>
  import {onMounted, ref} from 'vue'
  const filteredData = ref([])
  // Global variables
  let data = [];
  let selectedMovie = {};
  const currentFilter = ref('all')
  // const api = 'http://127.0.0.1:8000/movies';
  const api = '/api/movies';

  const titleInput = ref("")
  const directorInput = ref("")
  const releaseYearInput = ref("")
  const alreadyWatchedInput = ref()

  const editTitleInput = ref("")
  const editDirectorInput = ref("")
  const editReleaseYearInput = ref("")
  const editAlreadyWatchedInput = ref()

  function filterMovies(filter) {
    console.log("Filtering movies:", filter);
    currentFilter.value = filter;
    refreshMovies();
  }

  function tryEditMovie(id) {
    console.log("Editing movie:", id);
    const movie = data.find((x) => x.id === id);
    if (!movie) {
      console.error("Movie not found:", id);
      return;
    }

    selectedMovie = movie;

    editTitleInput.value = movie.title
    editDirectorInput.value = movie.director
    editReleaseYearInput.value = movie.release_year
    editAlreadyWatchedInput.value = movie.watched

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

  function addMovieInfo() {
    console.log("Form submitted");

    const title = titleInput.value
    const director = directorInput.value
    const year = releaseYearInput.value
    const watched = alreadyWatchedInput.value
    console.log("Adding movie:", title, director, year, watched);

    const editMsg = document.getElementById('edit-msg');
    if (!title) {
      if (editMsg) editMsg.innerHTML = 'Movie title cannot be blank';
      return;
    }
    if (!director) {
      if (editMsg) editMsg.innerHTML = 'Director name cannot be blank';
      return;
    }
    if (!year) {
      if (editMsg) editMsg.innerHTML = 'Release year cannot be blank';
      return;
    }
    fetch(api, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        title,
        director,
        release_year: parseInt(year),
        watched,
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
  }


  function editForm() {
    const title = editTitleInput.value
    const director = editDirectorInput.value
    const year = editReleaseYearInput.value
    const watched = editAlreadyWatchedInput.value
    console.log("Editing movie:", selectedMovie.id, title, director, year, watched);
    const editMsg = document.getElementById('edit-msg');
    if (!title) {
      if (editMsg) editMsg.innerHTML = 'Movie title cannot be blank';
      return;
    }
    if (!director) {
      if (editMsg) editMsg.innerHTML = 'Director name cannot be blank';
      return;
    }
    if (!year) {
      if (editMsg) editMsg.innerHTML = 'Release year cannot be blank';
      return;
    }
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
  }

    
  // helper functions
  function refreshMovies() {
    console.log("Refreshing movies with filter:", currentFilter);
    filteredData.value = [...data];

    if (currentFilter.value === 'watched') {
      filteredData.value = data.filter(movie => movie.watched);
    } else if (currentFilter.value === 'unwatched') {
      filteredData.value = data.filter(movie => !movie.watched);
    }
    console.log("Filtered data:", filteredData.value);
    filteredData.value
      .sort((a, b) => b.id - a.id)
  }

  function resetForm() {
    titleInput.value = ''
    directorInput.value = ''
    releaseYearInput.value = ''
    alreadyWatchedInput.value = ''

    editTitleInput.value = ''
    editDirectorInput.value = ''
    editReleaseYearInput.value = ''
    editAlreadyWatchedInput.value = ''
  }

  onMounted(() => {
    console.log("Getting movies from API");
    fetch(api)
      .then(response => {
        if (response.ok) {
          return response.json();
        }
        throw new Error(`Network response was not ok: ${response.statusText}`);
      })
      .then(movies => {
        console.log("Movies retrieved:", movies);
        data = movies || [];
        refreshMovies();
      })
      .catch(error => {
        console.error("Error getting movies:", error);
      });
  })
</script>

<template>
   <div class="container d-flex justify-content-center align-items-center" style="height: 100vh;">
    <div class="app">
      <h2 class="text-center mb-4">FilmTrack</h2>

      <div class="filter-buttons mb-3">
        <button @click="filterMovies('all')" class="btn btn-outline-primary">All Movies</button>
        <button @click="filterMovies('watched')" class="btn btn-outline-success">Watched</button>
        <button @click="filterMovies('unwatched')" class="btn btn-outline-warning">To Watch</button>
      </div>

      <div>
        <button type="button" class="btn btn-primary mb-3 w-100" data-bs-toggle="modal" data-bs-target="#addModal">
          <div id="addNew">
            <span>Add New Movie</span>
            <i class="fas fa-plus"></i>
          </div>
        </button>
      </div>


      <div v-for="movie in filteredData" :class="`movie-card ${movie.watched ? 'watched' : 'unwatched'}`">
        <div class="movie-header">
          <h4>{{movie.title}} ({{movie.release_year}})</h4>
          <span :class="`badge ${movie.watched ? 'bg-success' : 'bg-warning'}`">{{ movie.watched ? 'Watched' : 'To Watch' }}</span>
        </div>
        <p class="text-secondary">Director: {{movie.director}}</p>
        <div class="options">
          <i @click="toggleWatched(movie.id)" :class="`fas ${movie.watched ? 'fa-eye-slash' : 'fa-eye'}`"></i>
          <i @click="tryEditMovie(movie.id)" class="fas fa-edit" data-bs-toggle="modal" data-bs-target="#editModal"></i>
          <i @click="deleteMovie(movie.id)" class="fas fa-trash-alt"></i>
        </div>
      </div>
    </div>
  </div>


  <div class="modal fade" id="addModal" tabindex="-1" aria-labelledby="addModalLabel" aria-hidden="true">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="addModalLabel">Add New Movie</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close" id="add-close"></button>
        </div>
        <div class="modal-body">
          <form id="form-add">
            <div class="mb-3">
              <label for="title" class="form-label">Movie Title</label>
              <input type="text" class="form-control" id="title" v-model="titleInput">
            </div>
            <div class="mb-3">
              <label for="director" class="form-label">Director</label>
              <input type="text" class="form-control" id="director" v-model="directorInput">
            </div>
            <div class="mb-3">
              <label for="year" class="form-label">Release Year</label>
              <input type="number" class="form-control" id="year" v-model="releaseYearInput">
            </div>
            <div class="mb-3 form-check">
              <input type="checkbox" class="form-check-input" id="watched" v-model="alreadyWatchedInput">
              <label class="form-check-label" for="watched">Already Watched</label>
            </div>
            <div id="msg" class="mb-3"></div>
            <button type="button" class="btn btn-primary" @click="addMovieInfo()">Add Movie</button>
          </form>
        </div>
      </div>
    </div>
  </div>

  <div class="modal fade" id="editModal" tabindex="-1" aria-labelledby="editModalLabel" aria-hidden="true">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="editModalLabel">Edit Movie #<span id="movie-id"></span></h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close" id="edit-close"></button>
        </div>
        <div class="modal-body">
          <form id="form-edit">
            <div class="mb-3">
              <label for="title-edit" class="form-label">Movie Title</label>
              <input type="text" class="form-control" id="title-edit" v-model="editTitleInput">
            </div>
            <div class="mb-3">
              <label for="director-edit" class="form-label">Director</label>
              <input type="text" class="form-control" id="director-edit" v-model="editDirectorInput">
            </div>
            <div class="mb-3">
              <label for="year-edit" class="form-label">Release Year</label>
              <input type="number" class="form-control" id="year-edit" v-model="editReleaseYearInput">
            </div>
            <div class="mb-3 form-check">
              <input type="checkbox" class="form-check-input" id="watched-edit" v-model="editAlreadyWatchedInput">
              <label class="form-check-label" for="watched-edit">Already Watched</label>
            </div>
            <div id="edit-msg" class="mb-3"></div>
            <button type="button" class="btn btn-primary" @click="editForm()">Update Movie</button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/*  
header {
  line-height: 1.5;
}

.logo {
  display: block;
  margin: 0 auto 2rem;
}

@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }

  .logo {
    margin: 0 2rem 0 0;
  }

  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }
} */
html,
body {
  height: 100%;
  width: 100%;
  margin: 0;
  overflow: hidden;
  font-family: sans-serif;
  background-color: #e5e5e5;
}

.app {
  height: 100%;
  width: 500px;
  display: flex;
  flex-direction: column;
  background-color: #fff;
  border: 0.25rem solid #abcea1;
  border-radius: 0.5rem;
  padding: 1rem;
  overflow-y: auto;
}

#addNew {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: rgba(171, 206, 161, 0.35);
  padding: 5px 10px;
  border-radius: 5px;
  cursor: pointer;
}

.fa-plus {
  background-color: #abcea1;
  padding: 3px;
  border-radius: 3px;
}

#todos {
  display: flex;
  flex-direction: column;
  grid-template-columns: 1fr;
  gap: 14px;
  overflow-y: auto;
}

#todos div {
  border: 3px solid #abcea1;
  background-color: #e2eede;
  border-radius: 6px;
  padding: 5px;
  display: grid;
  gap: 4px;
}

#todos div .options {
  justify-self: center;
  display: flex;
  gap: 20px;
}

#todos div .options i {
  cursor: pointer;
}

#msg {
  color: red;
}

html,
body {
  height: 100%;
  width: 100%;
  margin: 0;
  overflow: hidden;
  font-family: sans-serif;
  background-color: #e5e5e5;
}

.app {
  height: 100%;
  width: 600px;
  display: flex;
  flex-direction: column;
  background-color: #fff;
  border: 0.25rem solid #5271ff;
  border-radius: 0.5rem;
  padding: 1rem;
  overflow-y: auto;
}

#addNew {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: rgba(82, 113, 255, 0.2);
  padding: 5px 10px;
  border-radius: 5px;
  cursor: pointer;
  border: none;
}

.fa-plus {
  background-color: #5271ff;
  color: white;
  padding: 3px;
  border-radius: 3px;
}

.filter-buttons {
  margin-bottom: 15px;
}

#movies {
  display: flex;
  flex-direction: column;
  gap: 14px;
  overflow-y: auto;
}

.movie-card {
  border: 3px solid #5271ff;
  background-color: #f0f5ff;
  border-radius: 6px;
  padding: 12px;
  display: grid;
  gap: 4px;
}

.movie-card.watched {
  border-color: #4CAF50;
  background-color: #f1f8e9;
}

.movie-card.unwatched {
  border-color: #FFC107;
  background-color: #fffde7;
}

.movie-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.options {
  justify-self: center;
  display: flex;
  gap: 20px;
  margin-top: 10px;
}

.options i {
  cursor: pointer;
  font-size: 1.2rem;
}

.fa-eye,
.fa-eye-slash {
  color: #5271ff;
}

.fa-edit {
  color: #FFC107;
}

.fa-trash-alt {
  color: #F44336;
}

#msg,
#edit-msg {
  color: red;
  font-size: 0.8rem;
}

.text-secondary {
  margin: 5px 0;
}
</style>
