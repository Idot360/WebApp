I have no clue.
This is  the original branch I work on. Most changes are pushed to this branch.
However, this cannot be directly ported over to pythonanywhere to host given differences in root directory.
To run, download all files/ clone the branch to local drive, and run the app.py file. The webapp will be hosted on [http://localhost:5000](http://localhost:5000)

Project Structure
--------

  ```sh
  ├── config.py
  ├── app.py
  ├── forms.py
  ├── data.py
  ├── forum.db
  ├── data.db
  ├── static
  │   ├── css
  │   │   └── main.css
  │   │   └── errors.css
  │   ├── ico
  │   │   ├── apple-touch-icon-114-precomposed.png
  │   │   ├── apple-touch-icon-144-precomposed.png
  │   │   ├── apple-touch-icon-57-precomposed.png
  │   │   ├── apple-touch-icon-72-precomposed.png
  │   │   └── favicon.png
  │   ├── img
  │   │   ├── gallery
  │   │   │   └── 
  │   │   └── home
  │   │   │   └── 
  │   │   └── meme
  │   │       └── 
  │   └── js
  │       └── konami.js
  └── templates
      ├── errors
      │   ├── 401.html
      │   ├── 403.html
      │   ├── 404.html
      │   └── 500.html
      ├── forms
      │   ├── login.html
      │   ├── post.html
      │   └── submit.html
      ├── layouts
      │   └── main.html
      └── pages
          ├── forum.html
          ├── gallery.html
          ├── approveabout.html
          ├── about.html
          ├── secret.html
          └── home.html
  ```



