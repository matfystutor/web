/*jshint esversion: 11 */
// this javascript file will swap the stylesheet.css to stylesheet_safari.css
// if the user is using the Safari browser

// get the stylesheet by the id "stylesheet"
const stylesheet = document.getElementById("stylesheet");

// check if the user is using Safari
if (navigator.userAgent.includes("Safari") && !navigator.userAgent.includes("Chrome")) {
    // if the user is using Safari, change the href attribute of the stylesheet to stylesheet_safari.css
    stylesheet.href = "/static/stylesheet_safari.css?v=1.2";
}

