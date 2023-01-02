
function showModal() {
  // Get the modal
  var modal = document.getElementById("myModal");

  // Show the modal
  modal.style.display = "block";

  // Hide the modal after 2 seconds
  setTimeout(function() {
    modal.style.display = "none";
  }, 2000);
}

const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))
