<script setup>
import { onMounted, ref } from "vue";
import icsDownloadImg from "@/assets/icsdownload.png"; // New: Import the image for the download button

const filteredData = ref([]);
// Global variables
let data = [];
let selectedMovie = {};
const currentFilter = ref("all");
const api = 'http://127.0.0.1:8000/movies';
// const api = "api/movies";

const titleInput = ref("");
const commentInput = ref(""); // Changed from directorInput
const ratingInput = ref(0); //Starting at 0
const reviewInput = ref(""); // Added review input for rating explanation
const alreadyWatchedInput = ref();

const editTitleInput = ref("");
const editCommentInput = ref(""); // Changed from editDirectorInput
const editRatingInput = ref(0);
const editReviewInput = ref(""); // Added edit review input
const editAlreadyWatchedInput = ref();

// Star Rating Hovering state
const hoverRating = ref(0);
const editHoverRating = ref(0);

// Reactive object to store viewing dates for each movie (keyed by movie.id)
const selectedDates = ref({});

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

  editTitleInput.value = movie.title;
  editCommentInput.value = movie.comment;
  editRatingInput.value = movie.rating;
  editReviewInput.value = movie.review || ""; // New: Load existing review
  editAlreadyWatchedInput.value = movie.watched;

  const editMsg = document.getElementById("edit-msg");
  if (editMsg) editMsg.innerHTML = "";
}

//Functions for Star Rating
function setRating(rating) {
  ratingInput.value = rating;
  hoverRating.value = 0;
}

function setEditRating(rating) {
  editRatingInput.value = rating;
  editHoverRating.value = 0;
}

function setHoverRating(rating) {
  hoverRating.value = rating;
}

function setEditHoverRating(rating) {
  editHoverRating.value = rating;
}

function clearHoverRating() {
  hoverRating.value = 0;
}

function clearEditHoverRating() {
  editHoverRating.value = 0;
}

function toggleWatched(id) {
  console.log("Toggling watched status for movie:", id);
  fetch(`${api}/${id}/toggle-watched`, {
    method: "PUT",
  })
    .then((response) => {
      if (response.ok) {
        const movie = data.find((x) => x.id === id);
        if (movie) {
          movie.watched = !movie.watched;
          refreshMovies();
        }
      } else {
        console.error("Error toggling watched status");
      }
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}

function deleteMovie(id) {
  console.log("Deleting movie:", id);
  fetch(`${api}/${id}`, {
    method: "DELETE",
  })
    .then((response) => {
      if (response.ok) {
        data = data.filter((x) => x.id !== id);
        refreshMovies();
      } else {
        console.error("Error deleting movie");
      }
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}

function addMovieInfo() {
  console.log("Form submitted");

  const title = titleInput.value;
  const comment = commentInput.value;
  const rating = ratingInput.value;
  const review = reviewInput.value;  
  const watched = !!alreadyWatchedInput.value;
  console.log("Adding movie:", title, comment, rating, review, watched); // Updated log message

  const msg = document.getElementById("msg");
  if (!title) {
    if (msg) msg.innerHTML = "Movie title cannot be blank";
    return;
  }
  
  fetch(api, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      title,
      comment,
      rating: parseInt(rating),
      review, // New: Include review in request body
      watched,
    }),
  })
    .then((response) => {
      console.log("Response status:", response.status);
      if (response.ok) {
        return response.json();
      }
      throw new Error("Network response was not ok: " + response.status);
    })
    .then((newMovie) => {
      console.log("Movie added successfully:", newMovie);
      data.push(newMovie);
      refreshMovies();
      resetForm();

      // Close modal
      const closeBtn = document.getElementById("add-close");
      if (closeBtn) {
        closeBtn.click();
      } else {
        console.error("Close button not found");
      }
    })
    .catch((error) => {
      console.error("Error adding movie:", error);
      if (msg) msg.innerHTML = "Error adding movie: " + error.message;
    });
}

function editForm() {
  const title = editTitleInput.value;
  const comment = editCommentInput.value;
  const rating = editRatingInput.value;
  const review = editReviewInput.value; // Get edit review input
  const watched = editAlreadyWatchedInput.value;
  console.log(
    "Editing movie:",
    selectedMovie.id,
    title,
    comment,
    rating,
    review,
    watched
  ); // Updated log message
  
  const editMsg = document.getElementById("edit-msg");
  if (!title) {
    if (editMsg) editMsg.innerHTML = "Movie title cannot be blank";
    return;
  }
  
  fetch(`${api}/${selectedMovie.id}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      title,
      comment,
      rating: parseInt(rating),
      review, // Include review in request body
      watched,
    }),
  })
    .then((response) => {
      if (response.ok) {
        selectedMovie.title = title;
        selectedMovie.comment = comment;
        selectedMovie.rating = parseInt(rating);
        selectedMovie.review = review; // Update review in selectedMovie
        selectedMovie.watched = watched;
        refreshMovies();
        const closeBtn = document.getElementById("edit-close");
        if (closeBtn) {
          closeBtn.click();
        }
      } else {
        console.error("Error updating movie");
        if (editMsg) editMsg.innerHTML = "Error updating movie";
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      if (editMsg) editMsg.innerHTML = "Error updating movie: " + error.message;
    });
}

// helper functions
// function refreshMovies() {
//   console.log("Refreshing movies with filter:", currentFilter);
//   filteredData.value = [...data];

//   if (currentFilter.value === "watched") {
//     filteredData.value = data.filter((movie) => movie.watched);
//   } else if (currentFilter.value === "unwatched") {
//     filteredData.value = data.filter((movie) => !movie.watched);
//   }
//   console.log("Filtered data:", filteredData.value);
//   filteredData.value.sort((a, b) => b.id - a.id);
// }

function resetForm() {
  titleInput.value = "";
  commentInput.value = "";
  ratingInput.value = "";
  reviewInput.value = ""; // New: Reset review input
  alreadyWatchedInput.value = "";

  editTitleInput.value = "";
  editCommentInput.value = "";
  editRatingInput.value = "";
  editReviewInput.value = ""; // New: Reset edit review input
  editAlreadyWatchedInput.value = "";
}

// Function to generate and download an ICS file for the movie viewing event
function downloadICS(movie) {
  // Retrieve the selected viewing date for this movie from the reactive selectedDates object
  const date = selectedDates.value[movie.id];
  if (!date) {
    // Alert the user if no date has been selected and exit the function
    alert("Please select a viewing date first!");
    return;
  }
  
  // Convert the selected date (format: YYYY-MM-DD) to ICS date format (YYYYMMDD)
  // Append a default start time (20:00 UTC) for the event
  const dtstart = date.replace(/-/g, "") + "T200000Z"; // Start at 20:00 UTC
  
  // Append a default end time (22:00 UTC) for the event
  const dtend = date.replace(/-/g, "") + "T220000Z";   // End at 22:00 UTC

  // Construct the ICS file content using the standard ICS format.
  // This includes the calendar metadata and event details like UID, timestamps, and event summary.
  const icsContent = `BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//FilmTrack//EN
BEGIN:VEVENT
UID:${movie.id}@filmtrack.com
DTSTAMP:${new Date().toISOString().replace(/[-:]/g, "").split('.')[0]}Z
DTSTART:${dtstart}
DTEND:${dtend}
SUMMARY:Watch ${movie.title}
DESCRIPTION:Reminder to watch ${movie.title}. Rating: ${movie.rating}/5. Comment: ${movie.comment}. Review: ${movie.review || "No review provided"}
END:VEVENT
END:VCALENDAR`;

  // Create a Blob object from the ICS content with the MIME type for calendar events
  const blob = new Blob([icsContent], { type: "text/calendar" });
  
  // Generate a temporary URL for the Blob
  const url = URL.createObjectURL(blob);
  
  // Create a temporary anchor element (<a>) and set its href attribute to the Blob URL
  const link = document.createElement("a");
  link.href = url;
  
  // Set the download attribute with a file name derived from the movie title
  link.download = `${movie.title.replace(/\s+/g, "_")}_reminder.ics`;
  
  // Append the anchor element to the document body to make it part of the DOM
  document.body.appendChild(link);
  
  // Programmatically click the link to trigger the download of the ICS file
  link.click();
  
  // Remove the temporary anchor element from the DOM after the download has started
  document.body.removeChild(link);
}


onMounted(() => {
  console.log("Getting movies from API");
  fetch(api)
    .then((response) => {
      if (response.ok) {
        return response.json();
      }
      throw new Error(`Network response was not ok: ${response.statusText}`);
    })
    .then((movies) => {
      console.log("Movies retrieved:", movies);
      data = movies;
      console.log("data: ", data)
      refreshMovies();
    })
    .catch((error) => {
      console.error("Error getting movies:", error);
    });
});
</script>

<template>
  <div class="container d-flex justify-content-center align-items-center" style="height: 100vh;">
    <div class="app">
      <h2 class="text-center mb-4">FilmTrack</h2>

      <div class="filter-buttons mb-3">
        <button @click="filterMovies('all')" class="btn btn-outline-primary">
          All Movies
        </button>
        <button
          @click="filterMovies('watched')"
          class="btn btn-outline-success"
        >
          Watched
        </button>
        <button
          @click="filterMovies('unwatched')"
          class="btn btn-outline-warning"
        >
          To Watch
        </button>
      </div>

      <div>
        <button
          type="button"
          class="btn btn-primary mb-3 w-100"
          data-bs-toggle="modal"
          data-bs-target="#addModal"
        >
          <div id="addNew">
            <span>Add New Movie</span>
            <i class="fas fa-plus"></i>
          </div>
        </button>
      </div>

      <!-- <div
        v-for="movie in filteredData"
        :key="movie.id"
        :class="`movie-card ${movie.watched ? 'watched' : 'unwatched'}`"
      >
        <div class="movie-header">
          <h4>{{ movie.title }} ({{ movie.rating }})</h4>
          <span :class="`badge ${movie.watched ? 'bg-success' : 'bg-warning'}`">
            {{ movie.watched ? "Watched" : "To Watch" }}
          </span>
        </div>
        <p class="text-secondary">Comment: {{ movie.comment }}</p>
        
        New: Rating review section showing why the user rated the movie as they did
        <div v-if="movie.review" class="rating-review">
          <h5>Why This Rating?</h5>
          <p>{{ movie.review }}</p>
        </div>
        
        <!-- Schedule viewing section with date picker and ICS download button
        <div class="schedule-viewing">
          <label :for="`watch-date-${movie.id}`" class="form-label">Select Viewing Date:</label>
          <input type="date" :id="`watch-date-${movie.id}`" v-model="selectedDates[movie.id]" class="form-control mb-2" />
          <img :src="icsDownloadImg" alt="Download Calendar" title="Download Calendar Event" @click="downloadICS(movie)" style="cursor: pointer; height: 40px;" />
          <span style="font-size: 0.9rem; margin-left: 10px;">Download Calendar Event</span>
        </div>
        <div class="options">
          <i
            @click="toggleWatched(movie.id)"
            :class="`fas ${movie.watched ? 'fa-eye-slash' : 'fa-eye'}`"
          ></i>
          <i
            @click="tryEditMovie(movie.id)"
            class="fas fa-edit"
            data-bs-toggle="modal"
            data-bs-target="#editModal"
          ></i>
          <i @click="deleteMovie(movie.id)" class="fas fa-trash-alt"></i>
        </div>
      </div> -->
    </div>
  </div>

  <div
    class="modal fade"
    id="addModal"
    tabindex="-1"
    aria-labelledby="addModalLabel"
    aria-hidden="true"
  >
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="addModalLabel">Add New Movie</h5>
          <button
            type="button"
            class="btn-close"
            data-bs-dismiss="modal"
            aria-label="Close"
            id="add-close"
          ></button>
        </div>
        <div class="modal-body">
          <form id="form-add">
            <div class="mb-3">
              <label for="title" class="form-label">Movie Title <i>(required)</i></label>
              <input type="text" class="form-control" id="title" v-model="titleInput" />
            </div>
            <div class="mb-3">
              <label for="comment" class="form-label">Comment</label>
              <input type="text" class="form-control" id="comment" v-model="commentInput" />
            </div>
            <div class="mb-3">
              <label for="rating" class="form-label">Rating <i>(1 to 5 stars)</i></label>
              <!-- Star Rating Component (add modal) -->
              <div class="star-rating">
                <span
                  v-for="i in 5"
                  :key="i"
                  class="star"
                  :class="{ filled: i <= (hoverRating || ratingInput) }"
                  @mouseover="setHoverRating(i)"
                  @mouseleave="clearHoverRating"
                  @click="setRating(i)"
                  >★</span
                >
              </div>
            </div>
            
            <!-- New: Review textarea for explaining the rating -->
            <div class="mb-3">
              <label for="review" class="form-label">Why this rating?</label>
              <textarea 
                class="form-control" 
                id="review" 
                v-model="reviewInput" 
                rows="3"
                placeholder="Explain why you gave this rating..."
              ></textarea>
            </div>
            
            <div class="mb-3 form-check">
              <input type="checkbox" class="form-check-input" id="watched" v-model="alreadyWatchedInput" />
              <label class="form-check-label" for="watched">Already Watched</label>
            </div>
            <div id="msg" class="mb-3"></div>
            <button type="button" class="btn btn-primary" @click="addMovieInfo()">Add Movie</button>
          </form>
        </div>
      </div>
    </div>
  </div>

  <div
    class="modal fade"
    id="editModal"
    tabindex="-1"
    aria-labelledby="editModalLabel"
    aria-hidden="true"
  >
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="editModalLabel">
            Edit Movie #<span id="movie-id"></span>
          </h5>
          <button
            type="button"
            class="btn-close"
            data-bs-dismiss="modal"
            aria-label="Close"
            id="edit-close"
          ></button>
        </div>
        <div class="modal-body">
          <form id="form-edit">
            <div class="mb-3">
              <label for="title-edit" class="form-label">Movie Title <i>(required)</i></label>
              <input type="text" class="form-control" id="title-edit" v-model="editTitleInput" />
            </div>
            <div class="mb-3">
              <label for="comment-edit" class="form-label">Comment</label>
              <input type="text" class="form-control" id="comment-edit" v-model="editCommentInput" />
            </div>
            <div class="mb-3">
              <label for="rating-edit" class="form-label">Rating <i>(1 to 5 stars)</i></label>
              <!-- Star Rating Component (edit modal)-->
              <div class="star-rating">
                <span
                  v-for="i in 5"
                  :key="i"
                  class="star"
                  :class="{ filled: i <= (editHoverRating || editRatingInput) }"
                  @mouseover="setEditHoverRating(i)"
                  @mouseleave="clearEditHoverRating"
                  @click="setEditRating(i)"
                  >★</span
                >
              </div>
              <input type="number" class="form-control" id="rating-edit" v-model="editRatingInput" />
            </div>
            
            <!-- New: Edit review text area for explaining the rating -->
            <div class="mb-3">
              <label for="review-edit" class="form-label">Why this rating?</label>
              <textarea 
                class="form-control" 
                id="review-edit" 
                v-model="editReviewInput" 
                rows="3"
                placeholder="Explain why you gave this rating..."
              ></textarea>
            </div>
            
            <div class="mb-3 form-check">
              <input type="checkbox" class="form-check-input" id="watched-edit" v-model="editAlreadyWatchedInput" />
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
  margin-bottom: 15px;
}

.movie-card.watched {
  border-color: #4caf50;
  background-color: #f1f8e9;
}

.movie-card.unwatched {
  border-color: #ffc107;
  background-color: #fffde7;
}

.movie-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* Styling for the rating review section */
.rating-review {
  margin-top: 10px;
  padding: 10px;
  background-color: rgba(255, 255, 255, 0.7);
  border-radius: 5px;
  border-left: 4px solid #5271ff;
}

.rating-review h5 {
  font-size: 1rem;
  margin-bottom: 5px;
  color: #333;
}

.rating-review p {
  font-style: italic;
  color: #555;
  margin-bottom: 0;
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
  color: #ffc107;
}

.fa-trash-alt {
  color: #f44336;
}

#msg,
#edit-msg {
  color: red;
  font-size: 0.8rem;
}

.text-secondary {
  margin: 5px 0;
}

/* For the Star Rating Component */
.star-rating {
  display: flex;
  margin: 5px 0;
}

.star {
  cursor: pointer;
  font-size: 30px;
  color: #cfcfcf;
  transition: color 0.2s;
  margin-right: 5px;
}

.star.filled {
  color: #ffd700;
}

.star-display {
  margin: 5px 0;
}

/* Style for the schedule viewing section */
.schedule-viewing {
  margin-top: 10px;
  padding: 10px;
  border-top: 1px solid #ccc;
}
</style>