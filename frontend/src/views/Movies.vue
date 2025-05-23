<template>

  <div :style="bgStyle" class="background-container">
    <div class="main-content">
      <div class="container d-flex justify-content-center align-items-center">
        <div class="app">
          <h2 class="text-center mb-4">FilmTrack</h2>
          <form @submit="uploadBackgroundImage" enctype="multipart/form-data">
            <div>
              <label for="photo">Choose background photo</label>
              <input type="file" id="photo" name="photo" @change="handleFileChange"/>
              <p v-if="fileSizeError" style="color: red;">{{ fileSizeError }}</p>
            </div>
            <div>
              <button type="submit">Submit</button>
            </div>
          </form>
          <div class="filter-buttons mb-3">
            <button @click="filterMovies('all')" class="btn btn-outline-primary">
              All Movies
            </button>
            <button
              @click="filterMovies('watched')"
              class="btn btn-outline-success"
            >
              My Watched
            </button>
            <button
              @click="filterMovies('not_watched')"
              class="btn btn-outline-warning"
            >
              My To Watch
            </button>
            <!-- New My Movies button -->
            <button @click="filterMovies('my')" class="btn btn-outline-secondary">
              My Movies
            </button>
          </div>

          <!-- Filter description -->
          <div class="filter-description mb-3 text-center">
            <span v-if="currentFilter === 'all'">
              <i class="fas fa-info-circle"></i> Showing all movies in the
              database
            </span>
            <span v-else-if="currentFilter === 'watched'">
              <i class="fas fa-check-circle"></i> Showing movies you've marked as
              watched
            </span>
            <span v-else-if="currentFilter === 'not_watched'">
              <i class="fas fa-clock"></i> Showing movies in your to-watch list
            </span>
            <span v-else-if="currentFilter === 'my'">
              <i class="fas fa-user"></i> Showing movies you've added to the
              database
            </span>
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

          <!-- No movies found message -->
          <div
            v-if="filteredData.length === 0"
            class="text-center p-4 bg-light rounded mb-3"
          >
            <i class="fas fa-film fa-2x mb-2 text-muted"></i>
            <p class="mb-0">No movies found for this filter.</p>
            <p class="text-muted" v-if="currentFilter !== 'all'">
              Try another filter or add some movies.
            </p>
          </div>

          <div
            v-for="movie in filteredData"
            :key="movie.id"
            :class="`movie-card ${
              movie.watched_status === 'watched' ? 'watched' : 'unwatched'
            }`"
          >
            <div class="movie-header">
              <div class="movie-title-rating">
                <h4>{{ movie.title }}</h4>
                <div class="movie-ratingidsplay">
                  <span class="star-rating-display">
                    {{ "★".repeat(movie.user_review?.rating || movie.rating || 0)
                    }}{{
                      "☆".repeat(
                        5 - (movie.user_review?.rating || movie.rating || 0)
                      )
                    }}
                  </span>
                </div>
              </div>
            </div>

            <!-- "Added by" information -->
            <div class="movie-metadata">
              <p class="added-by">
                <i class="fas fa-user"></i> Added by:
                <span class="user">{{ movie.added_by }}</span>
              </p>
              <p clas="added-date">
                <i class="fas fa-calendar-alt"></i> Added on:
                <span class="date">{{ formatDate(movie.date_added) }}</span>
              </p>
            </div>

            <p class="text-secondary">Comment: {{ movie.comment }}</p>

            <div
              v-if="movie.user_review?.review || movie.review"
              class="rating-review"
            >
              <h5>Why This Rating?</h5>
              <p>{{ movie.user_review?.review || movie.review }}</p>
            </div>

            <div class="schedule-viewing">
              <label :for="`movie-watch-date-${movie.id}`" class="form-label"
                >Select Viewing Date:</label
              >
              <input
                type="date"
                :id="`movie-watch-date-${movie.id}`"
                :name="`movie-watch-date-${movie.id}`"
                v-model="selectedDates[movie.id]"
                class="form-control mb-2"
              />
              <img
                :src="icsDownloadImg"
                alt="Download Calendar"
                title="Download Calendar Event"
                @click="downloadICS(movie)"
                style="cursor: pointer; height: 40px"
              />
              <span style="font-size: 0.9rem; margin-left: 10px"
                >Download Calendar Event</span
              >
            </div>
            <div class="options">
              <i
                v-if="isAdmin || movie.added_by === getUsernameFromToken()"
                @click="tryEditMovie(movie.id)"
                class="fas fa-edit"
                data-bs-toggle="modal"
                data-bs-target="#editModal"
                :title="
                  isAdmin && movie.added_by !== getUsernameFromToken()
                    ? 'Edit movie (admin)'
                    : 'Edit movie'
                "
                :class="{
                  'admin-action':
                    isAdmin && movie.added_by !== getUsernameFromToken(),
                }"
              ></i>
              <i
                v-else
                class="fas fa-edit disabled"
                title="You can only edit movies you added"
              ></i>

              <i
                v-if="isAdmin || movie.added_by === getUsernameFromToken()"
                @click="deleteMovie(movie.id)"
                class="fas fa-trash-alt"
                :title="
                  isAdmin && movie.added_by !== getUsernameFromToken()
                    ? 'Delete movie (admin)'
                    : 'Delete movie'
                "
                :class="{
                  'admin-action':
                    isAdmin && movie.added_by !== getUsernameFromToken(),
                }"
              ></i>
              <i
                v-else
                class="fas fa-trash-alt disabled"
                title="You can only delete movies you added"
              ></i>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
        <!-- Add new movie Modal -->
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
              <form id="form-add" @submit.prevent="addMovieInfo">
                <div class="mb-3">
                  <label for="add-movie-title" class="form-label"
                    >Movie Title <i>(required)</i></label
                  >
                  <input
                    type="text"
                    class="form-control"
                    id="add-movie-title"
                    name="add-movie-title"
                    v-model="titleInput"
                    required
                  />
                </div>
                <div class="mb-3">
                  <label for="add-movie-comment" class="form-label"
                    >Comment</label
                  >
                  <input
                    type="text"
                    class="form-control"
                    id="add-movie-comment"
                    name="add-movie-comment"
                    v-model="commentInput"
                  />
                </div>
                <div class="mb-3">
                  <label for="add-movie-rating" class="form-label"
                    >Rating <i>(1 to 5 stars)</i></label
                  >
                  <input
                    type="hidden"
                    id="add-movie-rating"
                    name="add-movie-rating"
                    :value="ratingInput"
                  />
                  <div
                    class="star-rating"
                    aria-labelledby="add-movie-rating-label"
                  >
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

                <div class="mb-3">
                  <label for="add-movie-review" class="form-label"
                    >Why this rating?</label
                  >
                  <textarea
                    class="form-control"
                    id="add-movie-review"
                    name="add-movie-review"
                    v-model="reviewInput"
                    rows="3"
                    placeholder="Explain why you gave this rating..."
                  ></textarea>
                </div>

                <div class="mb-3 form-check">
                  <input
                    type="checkbox"
                    class="form-check-input"
                    id="add-movie-watched"
                    name="add-movie-watched"
                    v-model="alreadyWatchedInput"
                  />
                  <label class="form-check-label" for="add-movie-watched"
                    >Already Watched</label
                  >
                </div>
                <div id="msg" class="mb-3"></div>
                <button type="submit" class="btn btn-primary">Add Movie</button>
              </form>
            </div>
          </div>
        </div>
      </div>

      <!-- Edit existing movie Modal -->
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
                Edit Movie
                <span v-if="isEditingAsAdmin" class="admin-edit-badge"
                  >Admin Edit</span
                >
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
              <form id="form-edit" @submit.prevent="editForm">
                <div class="mb-3">
                  <label for="edit-movie-title" class="form-label"
                    >Movie Title <i>(required)</i></label
                  >
                  <input
                    type="text"
                    class="form-control"
                    id="edit-movie-title"
                    name="edit-movie-title"
                    v-model="editTitleInput"
                    required
                  />
                </div>
                <div class="mb-3">
                  <label for="edit-movie-comment" class="form-label"
                    >Comment</label
                  >
                  <input
                    type="text"
                    class="form-control"
                    id="edit-movie-comment"
                    name="edit-movie-comment"
                    v-model="editCommentInput"
                  />
                </div>
                <div class="mb-3">
                  <label for="edit-movie-rating" class="form-label"
                    >Rating
                    <i
                      >(1 to 5 stars. feel free to leave blank if you don't want
                      to Rate the movie)</i
                    ></label
                  >
                  <input
                    type="hidden"
                    id="edit-movie-rating"
                    name="edit-movie-rating"
                    :value="editRatingInput"
                  />
                  <div
                    class="star-rating"
                    aria-labelledby="edit-movie-rating-label"
                  >
                    <span
                      v-for="i in 5"
                      :key="i"
                      class="star"
                      :class="{
                        filled: i <= (editHoverRating || editRatingInput),
                      }"
                      @mouseover="setEditHoverRating(i)"
                      @mouseleave="clearEditHoverRating"
                      @click="setEditRating(i)"
                      >★</span
                    >
                  </div>
                </div>

                <div class="mb-3">
                  <label for="edit-movie-review" class="form-label"
                    >Why this rating?</label
                  >
                  <textarea
                    class="form-control"
                    id="edit-movie-review"
                    name="edit-movie-review"
                    v-model="editReviewInput"
                    rows="3"
                    placeholder="Explain why you gave this rating..."
                  ></textarea>
                </div>

                <div class="mb-3 form-check">
                  <input
                    type="checkbox"
                    class="form-check-input"
                    id="edit-movie-watched"
                    name="edit-movie-watched"
                    v-model="editAlreadyWatchedInput"
                  />
                  <label class="form-check-label" for="edit-movie-watched"
                    >Already Watched</label
                  >
                </div>

                <div id="edit-msg" class="mb-3"></div>
                <button type="submit" class="btn btn-primary">
                  Update Movie
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
</template>

<script setup>
import { ref, onMounted, onBeforeMount, computed, watch, nextTick } from "vue";
import icsDownloadImg from "@/assets/icsdownload.png";
import { useRouter } from "vue-router";

const router = useRouter();
const token = ref(localStorage.getItem("access_token"));
const authHeaders = computed(() =>
  token.value ? { Authorization: `Bearer ${token.value}` } : {}
);


const fileInput = ref(null);
const fileSizeError = ref('');
const maxSizeInBytes = 500 * 1024; // 500 KB

const handleFileChange = (event) => {
  console.log("event: ", event)
  const file = event.target.files[0];
  console.log("file: ", file)

  if (file) {
    console.log("file.size: ", )
    if (file.size > maxSizeInBytes) {
      fileSizeError.value = 'File size must be 500KB or less.';
      // Optionally clear the input value
      if (fileInput.value) {
        fileInput.value.value = '';
      }
    } else {
      fileSizeError.value = '';
      // Proceed with handling the valid file
      console.log('Selected file:', file.name, 'Size:', file.size, 'bytes');
      // You might want to emit an event or update another ref with the file
    }
  } else {
    fileSizeError.value = ''; // No file selected, clear any error
  }
}
// Define a reactive variable to store the background image URL or a base64 string.
const backgroundImage = ref('')

// Create a computed style object for the container.
// This object will update whenever backgroundImage changes.
const bgStyle = computed(() => {
  return backgroundImage.value
    ? {
        backgroundImage: `url(${backgroundImage.value})`,
        backgroundSize: 'cover',
        backgroundRepeat: 'no-repeat',
        backgroundPosition: 'center'
      }
    : {}
})


async function fetchBackgroundImage() {
  console.log("fetchBackgroundImage called")
  try {
    const response = await fetch(`${api}/get-background-photo`, {
      headers: {
        ...authHeaders.value,
      }
    })

    console.log("fetch backgroundImage response: ", response)
    const data = await response.json()
    console.log("data: ", data)
    
    // Check if the photo is already formatted as a data URI
    if (data.photo && data.photo.trim() !== '') {
      // Add the data URI prefix if it doesn't already have one
      if (!data.photo.startsWith('data:image')) {
        backgroundImage.value = `data:image/jpeg;base64,${data.photo}`
      } else {
        backgroundImage.value = data.photo
      }
      console.log("backgroundImage.value is set")
    } else {
      console.log("No background image data received")
    }
  } catch (error) {
    console.error('Error fetching background image:', error)
  }
}

async function uploadBackgroundImage(event) {
  // Prevent the default form submission behavior
  event.preventDefault();
  
  // Get the file input element
  const fileInput = event.target.querySelector('#photo');

  // Check if a file was actually selected
  if (!fileInput.files.length) {
    console.log("No file selected");
    return;
  }
  
  // Create a FormData instance and append the first selected file
  const formData = new FormData();
  formData.append('photo', fileInput.files[0]);

  try {
    const response = await fetch(`${api}/upload-background-photo`, {
      method: "POST",
      headers: {
         ...authHeaders.value,
      },
      body: formData,
    });

    const result = await response.json();
    console.log("Upload response: ", result);
    await nextTick()
    fetchBackgroundImage()
  } catch (err) {
    console.error("Error uploading photo: ", err);
  }
}
// Watch for token changes
watch(
  () => localStorage.getItem("access_token"),
  (newToken) => {
    token.value = newToken;

    // If token is removed, redirect to login
    if (!newToken) {
      router.push("/login");
    }
  }
);

// Check for authentication before component mounts
onBeforeMount(() => {
  if (!token.value) {
    router.push("/login");
    return;
  }
});

const filteredData = ref([]);
let allMoviesData = [];
let selectedMovie = {};
const currentFilter = ref("all");
const api = "http://127.0.0.1:8000/movies";

// Form inputs
const titleInput = ref("");
const commentInput = ref("");
const ratingInput = ref(0);
const reviewInput = ref("");
const alreadyWatchedInput = ref(false);

const editTitleInput = ref("");
const editCommentInput = ref("");
const editRatingInput = ref(0);
const editReviewInput = ref("");
const editAlreadyWatchedInput = ref(false);

// Star Rating Hovering state
const hoverRating = ref(0);
const editHoverRating = ref(0);

// Reactive object to store viewing dates for each movie
const selectedDates = ref({});

// Admin state - track if current user is an admin
const userRole = ref(localStorage.getItem("user_role") || "BasicUser");
const isEditingAsAdmin = ref(false);
const isAdmin = computed(() => {
  // First check local storage directly
  if (userRole.value === "AdminUser") {
    return true;
  }

  // Then verify with JWT token
  const tokenAdmin = checkAdminRole();
  if (tokenAdmin) {
    // If the token says we're admin but localStorage doesn't, update localStorage
    if (userRole.value !== "AdminUser") {
      userRole.value = "AdminUser";
      localStorage.setItem("user_role", "AdminUser");
    }
    return true;
  }

  return false;
});

// Check if user has admin role from JWT token
// Improved admin role check function
function checkAdminRole() {
  const token = localStorage.getItem("access_token");
  if (!token) return false;

  try {
    const payload = token.split(".")[1];
    const decodedPayload = atob(payload);
    const payloadData = JSON.parse(decodedPayload);

    console.log("Token payload:", payloadData); // For debugging

    // Check if the role is AdminUser
    return payloadData.role === "AdminUser";
  } catch (e) {
    console.error("Error checking admin role:", e);
    return false;
  }
}

// Function to format date - added for displaying date_added
function formatDate(dateString) {
  if (!dateString) return "Unknown";

  const date = new Date(dateString);
  return new Intl.DateTimeFormat("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "numeric",
    hour12: true,
  }).format(date);
}

function filterMovies(filter) {
  currentFilter.value = filter;
  const filter2 = currentFilter.value;
  refreshMovies(filter2);
}

async function tryEditMovie(id) {
  // Get movie data by id
  const response = await fetch(`${api}/get/${id}`, {
    method: "GET",
    headers: {
      ...authHeaders.value,
    },
  });

  // Check HTTP response
  if (!response.ok) {
    console.error("Error fetching movie:", response.status);
    showUpdateErrorModal(`Failed to fetch movie: ${response.statusText}`);
    return;
  }

  const movie = await response.json();
  isEditingAsAdmin.value =
    isAdmin.value && movie.added_by !== getUsernameFromToken();
  selectedMovie = movie;

  // Populate form fields
  editTitleInput.value = movie.title;
  editCommentInput.value = movie.comment || "";

  // Handle rating field - check all possible locations
  if (movie.user_review && typeof movie.user_review.rating === "number") {
    editRatingInput.value = movie.user_review.rating;
  } else if (typeof movie.rating === "number") {
    editRatingInput.value = movie.rating;
  } else {
    editRatingInput.value = 0;
  }

  // Handle review text - check all possible locations
  if (movie.user_review && movie.user_review.review) {
    editReviewInput.value = movie.user_review.review;
  } else if (movie.review) {
    editReviewInput.value = movie.review;
  } else {
    editReviewInput.value = "";
  }

  editAlreadyWatchedInput.value = movie.watched_status === "watched";

  const editMsg = document.getElementById("edit-msg");
  if (editMsg) editMsg.innerHTML = "";
}

// Star Rating Functions
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

function deleteMovie(id) {
  const movie = filteredData.value.find((movie) => movie.id === id);
  if (!movie) {
    console.error("Movie not found", id);
    return;
  }

  const username = getUsernameFromToken();
  const isAdminDeleting =
    isAdmin.value && movie.added_by !== getUsernameFromToken();

  let confirmMessage = "Are you sure you want to delete this movie?";
  if (isAdminDeleting) {
    confirmMessage = `ADMIN ACTION: Are you sure you wat to delete "${movie.title}" added by ${movie.added_by}?`;
  }
  if (!confirm(confirmMessage)) {
    return;
  }

  fetch(`${api}/${id}`, {
    method: "DELETE",
    headers: {
      ...authHeaders.value,
    },
  })
    .then((response) => {
      if (response.ok) {
        refreshMovies();
        return { success: true };
      } else if (response.status === 403) {
        return response.json().then((data) => {
          return {
            success: false,
            error:
              data.detail || "You don't have permission to delete this movie",
          };
        });
      } else {
        return { success: false, error: "Error deleting movie" };
      }
    })
    .then((result) => {
      if (!result.success) {
        showDeleteErrorModal(result.error);
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      showDeleteErrorModal("An unexpected error occurred");
    });
}

function showDeleteErrorModal(errorMessage) {
  const modalMessage = `
    ${errorMessage}. 
    If you believe this movie contains inappropriate content, 
    please email admin to report it.
  `;

  alert(modalMessage);
}

function addMovieInfo() {
  // prepare api inputs, initialize to empty srings if user left blank
  const title = titleInput.value || "";
  const comment = commentInput.value || "";
  const rating = ratingInput.value;
  const review = reviewInput.value || "";
  const watched = alreadyWatchedInput.value ? "watched" : "not_watched";

  // message indicating required fields
  const msg = document.getElementById("msg");
  if (!title) {
    if (msg) msg.innerHTML = "Movie title cannot be blank";
    return;
  }

  // add movie info to database
  fetch(api, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders.value,
    },
    body: JSON.stringify({
      movie: {
        title,
        comment,
      },
      watchlist: {
        watched_status: watched,
      },
      review: {
        rating: parseInt(rating),
        review,
      },
    }),
  })
    .then((response) => {
      if (response.ok) {
        return response.json();
      }
      throw new Error("Network response was not ok: " + response.status);
    })
    .then((newMovie) => {
      refreshMovies();
      resetForm();

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
  // initiallize api inputs based on values from form, default to empty strings for fields left blank
  const title = editTitleInput.value || "";
  const comment = editCommentInput.value || "";
  const rating = editRatingInput.value;
  const review = editReviewInput.value || "";
  const watched = editAlreadyWatchedInput.value ? "watched" : "not_watched";

  // indicate required field left blank
  const editMsg = document.getElementById("edit-msg");
  if (!title) {
    if (editMsg) editMsg.innerHTML = "Movie title cannot be blank";
    return;
  }

  // Check if the current user is the one who added the movie
  const username = getUsernameFromToken();
  if (!isAdmin.value && selectedMovie.added_by !== getUsernameFromToken()) {
    if (editMsg) editMsg.innerHTML = "You can only edit movies that you added";
    return;
  }

  // update existing items in database
  fetch(`${api}/${selectedMovie.id}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders.value,
    },
    body: JSON.stringify({
      movie: {
        title,
        comment,
      },
      watchlist: {
        watched_status: watched,
      },
      review: {
        rating: parseInt(rating),
        review,
      },
    }),
  })
    .then((response) => {
      if (response.ok) {
        refreshMovies();
        const closeBtn = document.getElementById("edit-close");
        if (closeBtn) {
          closeBtn.click();
        }
        return { success: true };
      } else if (response.status === 403) {
        return response.json().then((data) => {
          return {
            success: false,
            error:
              data.detail || "You don't have permission to update this movie",
          };
        });
      } else {
        return { success: false, error: "Error updating movie" };
      }
    })
    .then((result) => {
      if (!result.success) {
        showUpdateErrorModal(result.error);
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      if (editMsg) editMsg.innerHTML = "Error updating movie: " + error.message;
    });
}

// Extract username from JWT token
function getUsernameFromToken() {
  const token = localStorage.getItem("access_token");
  if (!token) return null;

  try {
    // JWT tokens are base64 encoded in 3 parts: header.payload.signature
    const payload = token.split(".")[1];
    // Decode the base64 payload
    const decodedPayload = atob(payload);
    // Parse the JSON
    const payloadData = JSON.parse(decodedPayload);
    // Return the username (could be in the 'sub' or 'username' field)
    return payloadData.username || payloadData.sub;
  } catch (e) {
    console.error("Error decoding token", e);
    return null;
  }
}

function showUpdateErrorModal(errorMessage) {
  const modalMessage = `
    ${errorMessage}. 
    If you believe this movie contains inappropriate content, 
    please email admin to report it.
  `;

  alert(modalMessage);

  // Close the edit modal after showing the error
  const closeBtn = document.getElementById("edit-close");
  if (closeBtn) {
    closeBtn.click();
  }
}

function refreshMovies() {
  // initialize watched_status for use in api call to determine which items to return (all, watched, not watched, or my)
  const watched_status = currentFilter.value;
  fetch(`${api}/${watched_status}`, {
    headers: {
      ...authHeaders.value,
    },
  })
    .then((response) => {
      if (response.status === 401) {
        localStorage.removeItem("access_token");
        token.value = null;
        router.push("/login");
        return null;
      }

      if (response.ok) {
        return response.json();
      }
      throw new Error(`Network response was not ok: ${response.statusText}`);
    })
    .then((movies) => {
      if (!movies) return;
      filteredData.value = movies; // Store all movies

      // Check if the user is an admin
      if (movies.length > 0 && movies[0].hasOwnProperty("is_admin")) {
        isAdmin.value = movies[0].is_admin;
      } else {
        // Fallback to checking the JWT token
        isAdmin.value = checkAdminRole();
      }

      console.log("User is admin: ", isAdmin.value);
    })
    .catch((error) => {
      console.error("Error getting movies:", error);
    });
}

function resetForm() {
  titleInput.value = "";
  commentInput.value = "";
  ratingInput.value = 0;
  reviewInput.value = "";
  alreadyWatchedInput.value = false;

  editTitleInput.value = "";
  editCommentInput.value = "";
  editRatingInput.value = 0;
  editReviewInput.value = "";
  editAlreadyWatchedInput.value = false;
}

function downloadICS(movie) {
  const date = selectedDates.value[movie.id];
  if (!date) {
    alert("Please select a viewing date first!");
    return;
  }

  const dtstart = date.replace(/-/g, "") + "T200000Z";
  const dtend = date.replace(/-/g, "") + "T220000Z";

  // Use the user_review rating if available
  const ratingText = movie.user_review
    ? `Rating: ${movie.user_review.rating}/5`
    : `Rating: Not rated yet`;

  // Use the user_review review if available, otherwise use movie.review
  const reviewText =
    movie.user_review?.review || movie.review || "No review provided";

  const icsContent = `BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//FilmTrack//EN
BEGIN:VEVENT
UID:${movie.id}@filmtrack.com
DTSTAMP:${new Date().toISOString().replace(/[-:]/g, "").split(".")[0]}Z
DTSTART:${dtstart}
DTEND:${dtend}
SUMMARY:Watch ${movie.title}
DESCRIPTION:Reminder to watch ${movie.title}. ${ratingText}. Comment: ${
    movie.comment
  }. Review: ${reviewText}
END:VEVENT
END:VCALENDAR`;

  const blob = new Blob([icsContent], { type: "text/calendar" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `${movie.title.replace(/\s+/g, "_")}_reminder.ics`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

// Make sure token is refreshed at mount time
onMounted(() => {
  token.value = localStorage.getItem("access_token");
  userRole.value = localStorage.getItem("user_role") || "BasicUser";

  console.log("Movies.vue mounted, user role:", userRole.value);
  console.log("Admin from token:", checkAdminRole());
  console.log("Is admin (computed):", isAdmin.value);

  if (!token.value) {
    router.push("/login");
    return;
  }

  refreshMovies();
  fetchBackgroundImage()

});
</script>

<style scoped>

.background-container {
  width: 100vw;
  position: absolute;
  left: 50%;
  top: 58%;
  transform: translate(-50%, -50%);
}
/* Styles remain unchanged */
html,
body {
  height: 100%;
  width: 100%;
  margin: 0;
  overflow: hidden;
  font-family: sans-serif;
  background-color: #e5e5e5;
}

.main-content {
  padding-top: 20px;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  width: 100%;
}

.app {
  width: 600px;
  max-width: 100%;
  display: flex;
  flex-direction: column;
  background-color: #fff;
  border: 0.25rem solid #5271ff;
  border-radius: 0.5rem;
  padding: 1rem;
  overflow-y: auto;
  max-height: 90vh;
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
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.filter-buttons button {
  flex: 1;
  min-width: 100px;
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
.movie-title-rating {
  display: flex;
  flex-direction: column;
  width: 100%;
}

.movie-title-rating h4 {
  margin-bottom: 5px;
}

.movie-rating-banner {
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  padding: 4px 8px;
  border-radius: 4px;
  margin-top: 4px;
  border-left: 4px solid #ffd700;
}

.movie-rating .star-display {
  color: #ffd700;
  font-size: 1.2rem;
  margin-left: 10px;
}

.text-secondary {
  margin: 5px 0;
}

.star-rating-display {
  color: #ffd700;
  font-size: 1.5rem;
  letter-spacing: 2px;
}

.rating-value {
  margin-left: 8px;
  font-weight: bold;
  color: #555;
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

.schedule-viewing {
  margin-top: 10px;
  padding: 10px;
  border-top: 1px solid #ccc;
}

.fas.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.notification-banner {
  background-color: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
  padding: 10px 0;
  width: 100%;
  position: sticky;
  top: 70% px;
  z-index: 100;
}

.notification-text {
  margin: 0;
  text-align: center;
  color: #6c757d;
  font-size: 0.9rem;
}

.notification-text i {
  margin-right: 5px;
  color: #5271ff;
}

.movie-metadata {
  background-color: rgba(0, 0, 0, 0.05); /* Very light background */
  padding: 8px 12px;
  border-radius: 4px;
  margin-bottom: 8px;
  font-size: 0.9rem;
  /* made a subtle border instead of dark background */
  border: 1px solid rgba(0, 0, 0, 0.1);
}

/* Using darker colors for lighter backgrounds */
.movie-metadata p {
  margin: 4px 0;
  display: flex;
  align-items: center;
  color: #333;
}

.movie-metadata i {
  margin-right: 8px;
  width: 16px;
  color: #5271ff;
}

.movie-metadata .user {
  font-weight: bold;
  color: #5271ff;
}

.movie-metadata .date {
  font-weight: bold;
}

.admin-badge {
  background-color: #dc3545;
  color: white;
  padding: 5px 10px;
  border-radius: 5px;
  font-weight: bold;
  text-align: center;
  margin: 10px auto;
  max-width: 250px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  box-shadow: 0 2pz 4px rgba(0, 0, 0, 0.2);
}

.admin-badge i {
  font-size: 1.2rem;
}

.admin-action {
  background-color: rgba(220, 53, 69, 0.1);
  color: #dc3545 !important;
  padding: 5px;
  border-radius: 50%;
}

.admin-edit-badge {
  font-size: 0.7rem;
  background-color: #dc3545;
  color: white;
  padding: 2px 5px;
  border-radius: 3px;
  margin-left: 5px;
  vertical-align: middle;
}

.filter-description {
  background-color: #f8f9fa;
  padding: 8px;
  border-radius: 4px;
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 15px;
  border: 1px solid #e9ecef;
}

.filter-description i {
  margin-right: 5px;
  color: #5271ff;
}

@media (max-width: 768px) {
  .app {
    width: 95%;
    margin: 0 auto;
  }

  .filter-button {
    flex-direction: row;
    flex-wrap: wrap;
  }

  .filter-buttons buttons {
    flex: 1 0 45%;
    margin-bottom: 5px;
  }
}
</style>
