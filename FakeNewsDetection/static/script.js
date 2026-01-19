document.addEventListener("DOMContentLoaded", function () 
{
    fetchTrendingNews();
});

function truncateText(text, maxLength) {
    return text.length > maxLength ? text.substring(0, maxLength) + "..." : text;
}
async function fetchTrendingNews() {
    try {
        const response = await fetch("/fetch-news");  // Fetch data from backend
        const newsData = await response.json();

        const newsContainer = document.getElementById("news-container");
        newsContainer.innerHTML = ""; // Clear existing content

        newsData.forEach(news => {
            const newsBox = document.createElement("div");
            newsBox.classList.add("fact-box");

            newsBox.innerHTML = `
                <img src="${news.image || 'static/default-news.jpg'}" alt="News Image" class="news-img">
                 <h3>${truncateText(news.title, 80)}</h3>
            `;

            // Open news link on click
            newsBox.addEventListener("click", () => {
                window.open(news.url, "_blank");
            });

            newsContainer.appendChild(newsBox);
        });
    } catch (error) {
        console.error("Error fetching news:", error);
    }
}



function searchNews() {
    let query = document.getElementById('search-input').value;
    if (!query) {
        alert("Please enter a search query!");
        return;
    }
    document.getElementById('loading').style.display = 'block'; // Show loading
    document.getElementById('news-grid').innerHTML = ''; // Clear old results

    fetch(`/search-news?q=${query}`)
    .then(response => response.json())
    .then(data => {
        document.getElementById('loading').style.display = 'none'; // Hide loading

        let newsGrid = document.getElementById('news-grid');
        newsGrid.innerHTML = ''; // Clear previous results

        if (data.length === 0) {
            newsGrid.innerHTML = '<p>No news found for this topic.</p>';
            return;
        }

        let maxItems = Math.min(data.length, 6); // Limit to 6 results

        data.slice(0, maxItems).forEach((news, index) => {
            let newsItem = document.createElement('div');
            newsItem.classList.add('news-item');
            if (index >= 3) newsItem.classList.add('hidden'); // Hide extra items initially

            let imageUrl = news.image && news.image !== 'None' ? news.image : 'default-news.jpg'; // Default image

            newsItem.innerHTML = `
                <a href="${news.url}" target="_blank">
                    <img src="${imageUrl}" alt="News Image">
                    <h3>${news.title}</h3>
                    <p>${formatDate(news.published_date)}</p>
                </a>
            `;
            newsGrid.appendChild(newsItem);
        });

        document.getElementById('see-more-btn').style.display = data.length > 3 ? 'block' : 'none';
    })
    .catch(error => {
        document.getElementById('loading').style.display = 'none'; // Hide loading
        console.error("Error fetching news:", error);
    });
}


function expandNews() {
    document.querySelectorAll('.news-item.hidden').forEach(item => {
        item.classList.remove('hidden');
    });
    document.getElementById('see-more-btn').style.display = 'none';
}


function formatDate(dateString) {
    let options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('en-IN', options); // Format in Indian date format
}


