
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
