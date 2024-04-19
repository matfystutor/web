/*jshint esversion: 11 */

function switchTheme() {
    "use strict";
    const isLightMode = document.documentElement.classList.contains("light");
    document.documentElement.classList.toggle("light", !isLightMode);
    document.documentElement.classList.toggle("dark", isLightMode);
    localStorage.setItem("lightMode", !isLightMode);
    localStorage.setItem("darkMode", isLightMode);
}

function setTheme() {
    "use strict";
    const prefersDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const isDarkMode = localStorage.getItem("darkMode") === "true" || (localStorage.getItem("darkMode") !== "false" && prefersDarkMode);

    document.documentElement.classList.toggle("dark", isDarkMode);
    document.documentElement.classList.toggle("light", !isDarkMode);
}

