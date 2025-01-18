// Fungsi untuk menangani perubahan pada file input
// Log untuk memastikan file script.js dimuat
console.log("Script.js loaded successfully");

// Deteksi halaman berdasarkan URL
const currentPage = window.location.pathname;

// Logika untuk index.html
if (currentPage.includes("index.html") || currentPage === "/") {
  console.log("Index page detected");

  const fileInput = document.getElementById("file-input");

  // Tangani perubahan pada file input
  if (fileInput) {
    fileInput.addEventListener("change", (event) => {
      const reader = new FileReader();
      const iconContainer = document.getElementById("icon-container");
      const uploadedImage = document.getElementById("uploaded-image");

      // Tampilkan pratinjau gambar
      if (event.target.files && event.target.files[0]) {
        reader.onload = () => {
          uploadedImage.src = reader.result;
          uploadedImage.style.display = "block";
          iconContainer.style.display = "none";
        };
        reader.readAsDataURL(event.target.files[0]);

        // Buat FormData dan tambahkan file yang diunggah
        const formData = new FormData();
        formData.append("file", event.target.files[0]);

        // Kirim data ke backend untuk prediksi
        fetch("http://localhost:8080/upload", {
          method: "POST",
          body: formData,
        })
          .then((response) => {
            if (!response.ok) {
              throw new Error(`Gagal memproses gambar. Status: ${response.status}`);
            }
            return response.json();
          })
          .then((result) => {
            if (result.error) {
              throw new Error(result.error);
            }

            // Tentukan warna berdasarkan status kematangan
            const color = result.prediction === "Matang" ? "Kuning" : "Hijau";

            // Tampilkan hasil prediksi di UI
            document.getElementById("color").innerText = color;
            document.getElementById("result").innerText = result.prediction;

            // Tambahkan gambar dan hasil ke history
            addToHistory({
              image: uploadedImage.src,
              color: color,
              status: result.prediction,
            });
          })
          .catch((error) => {
            console.error("Error:", error);
            document.getElementById("result").innerText = "Gagal memproses gambar";
            document.getElementById("color").innerText = "-";
          });
      } else {
        console.error("No file selected");
      }
    });
  } else {
    console.warn("File input element not found on index.html");
  }
}

// Logika untuk history.html
if (currentPage.includes("history.html")) {
  console.log("History page detected");

  const historyCards = document.getElementById("history-cards");

  if (!historyCards) {
    console.error("Element with ID 'history-cards' not found");
  } else {
    console.log("Element 'history-cards' ditemukan");

    // Kosongkan konten lama sebelum menambahkan data baru
    historyCards.innerHTML = "";

    // Fetch data history dari backend
    fetch("http://localhost:8080/get-history")
      .then((response) => {
        console.log("Fetch response:", response);
        if (!response.ok) {
          throw new Error("Failed to fetch history data");
        }
        return response.json();
      })
      .then((data) => {
        console.log("Data fetched:", data);

        const totalCards = Math.max(data.length, 10); // Minimal 10 kartu
        for (let i = 0; i < totalCards; i++) {
          const card = document.createElement("div");
          card.classList.add("history-card");

          // Jika ada data, tampilkan konten kartu
          if (data[i]) {
            card.innerHTML = `
              <img src="${data[i].image}" alt="Uploaded Image" />
              <p>Warna: ${data[i].color}</p>
              <p>Status: ${data[i].status}</p>
            `;
          } else {
            // Jika tidak ada data, tampilkan kartu kosong
            card.innerHTML = `
              <p style="color: #ccc; font-size: 1.2em; margin: auto">Kosong</p>
            `;
          }

          historyCards.appendChild(card);
        }
      })
      .catch((error) => {
        console.error("Error fetching history:", error);
      });
  }
}

// Fungsi untuk menambahkan data ke history secara lokal
function addToHistory(item) {
  const historyCards = document.getElementById("history-cards");
  if (!historyCards) {
    console.warn("History container not found, skipping addition");
    return;
  }

  const card = document.createElement("div");
  card.classList.add("history-card");
  card.innerHTML = `
    <img src="${item.image}" alt="Uploaded Image" />
    <p>Warna: ${item.color}</p>
    <p>Status: ${item.status}</p>
  `;
  historyCards.appendChild(card);
}
