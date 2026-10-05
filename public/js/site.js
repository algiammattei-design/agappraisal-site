// Quote form: submits to Web3Forms without leaving the page.
// Without JavaScript the form still posts normally and Web3Forms shows its own confirmation.
(function () {
  var form = document.querySelector("form.quote");
  if (!form) return;
  var status = form.querySelector(".form-status");
  var button = form.querySelector("button[type=submit]");

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    button.disabled = true;
    status.textContent = "Sending…";
    fetch(form.action, {
      method: "POST",
      headers: { Accept: "application/json" },
      body: new FormData(form)
    })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        if (data.success) {
          form.reset();
          status.textContent = "Thank you. Your request is in, and Al will be in touch with a quote.";
        } else {
          throw new Error(data.message || "failed");
        }
      })
      .catch(function () {
        status.textContent = "That did not go through. Please call or text (407) 588-7197, or email algiammattei@gmail.com.";
      })
      .finally(function () { button.disabled = false; });
  });

  // Close the mobile menu after a link is tapped.
  document.querySelectorAll(".menu nav a").forEach(function (a) {
    a.addEventListener("click", function () { a.closest("details").removeAttribute("open"); });
  });
})();
