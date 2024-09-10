const codes = [
  "ArrowUp", "ArrowUp", "ArrowDown", "ArrowDown", "ArrowLeft", "ArrowRight", "ArrowLeft", "ArrowRight", "b", "a"
];

let index = 0;

document.addEventListener("keydown", (e) => {
  const key = e.key;

  if (key === codes[index]) {
    index++;

    if (index === codes.length) {
      konami();

      index = 0;
    }
  } else {
    index = 0;
  }
});

function konami() {
    fetch('/trigger', {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'Content-Type': 'application/json'
                 }
        
    })
    .then(response => response.json())
    .then(data => {
        if (data.redirect) {
            window.location.href = data.redirect;
        } else {
            console.log(data.message);
        }
    })
    .catch(error => console.error('Error:', error));
  }