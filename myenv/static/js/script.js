
// code for form validation
document.querySelector('form').addEventListener('submit', function(event) {
    var password = document.getElementById('password').value;
    var confirmPassword = document.getElementById('confirmPassword').value;
  
    if (password !== confirmPassword) {
      event.preventDefault(); // Prevent form submission
      alert('Passwords do not match!');
    }
  });
  