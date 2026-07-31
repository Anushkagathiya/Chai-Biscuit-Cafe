document.getElementById("orderForm").addEventListener("submit", function (event) {
    event.preventDefault();
  
    const name = document.getElementById("name").value;
    const mobile = document.getElementById("mobile").value;
    const address = document.getElementById("address").value;
    const items = document.getElementById("items").value;
    const quantity = document.getElementById("quantity").value;
  
    if (name && mobile && address && items && quantity > 0) {
      alert("Your order has been placed successfully!");
      // Back-end ko data bhejne ka code yaha add hoga
    } else {
      alert("Please fill all the fields correctly.");
    }
  });
document.getElementById('contactForm').addEventListener('submit', function(event) {
    event.preventDefault();
    document.getElementById('formMessage').textContent = "Thank you for contacting us! We'll get back to you soon.";
});


