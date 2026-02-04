window.addEventListener("load", () => {
  setTimeout(() => {
    const splash = document.getElementById("splash");
    splash.classList.add("fade-out");

    setTimeout(() => {
      // Redirect to login page
      window.location.href = "login.html";
    }, 800);

  }, 2000); // splash duration
});
