document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("activityForm");
  const apiUrl = "http://127.0.0.1:5000"; // Update if deployed

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const name = document.getElementById("name").value;
    const email = document.getElementById("email").value;
    const phone = document.getElementById("phone").value;

    const distance = Number(document.querySelector("input[name='distance']").value);
    const transport = document.querySelector("select[name='transport']").value;
    const phoneUsage = Number(document.querySelector("input[name='phoneUsage']").value);
    const laptopUsage = Number(document.querySelector("input[name='laptopUsage']").value);

    // Prepare activity data
    const activityData = {
      name,
      email,
      phone,
    };

    // Assign transport values
    activityData.car_km = transport === "car" ? distance : 0;
    activityData.bus_km = transport === "bus" ? distance : 0;
    activityData.bike_km = transport === "bike" ? distance : 0;

    activityData.phone_hrs = phoneUsage;
    activityData.laptop_hrs = laptopUsage;

    try {
      const response = await fetch(`${apiUrl}/submit_activity`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(activityData)
      });

      if (!response.ok) {
        throw new Error("Failed to submit activity.");
      }

      const result = await response.json();

      if (result.status === "success") {
        showPieChart(result.emissions);
        showRecommendation(result.trees_to_plant);
        fetchAndDrawLineChart(email);
      } else {
        alert("Failed to calculate emissions.");
      }

    } catch (error) {
      console.error("Error:", error);
      alert("Server error. Please try again later.");
    }
  });

  // Pie Chart
  function showPieChart(emissions) {
    const ctx = document.getElementById("pieChart").getContext("2d");

    new Chart(ctx, {
      type: "pie",
      data: {
        labels: ["Transport", "Phone", "Laptop"],
        datasets: [{
          data: [emissions.transport, emissions.phone, emissions.laptop],
          backgroundColor: ["#4CAF50", "#2196F3", "#FFC107"]
        }]
      },
      options: {
        plugins: {
          title: {
            display: true,
            text: "Carbon Emission Breakdown (kg CO₂)"
          }
        }
      }
    });
  }

  // Tree Recommendation
  function showRecommendation(trees) {
    document.getElementById("recommendation").innerText =
      `You should plant approximately ${trees} tree(s) to offset today’s emissions 🌳`;
  }

  // Line Chart for Progress
  async function fetchAndDrawLineChart(email) {
    const res = await fetch(`${apiUrl}/get_progress?email=${encodeURIComponent(email)}`);
    const data = await res.json();

    const labels = data.history.map(entry => entry.date);
    const values = data.history.map(entry => entry.total_emission);

    const ctx = document.getElementById("lineChart").getContext("2d");

    new Chart(ctx, {
      type: "line",
      data: {
        labels: labels,
        datasets: [{
          label: "Daily Emissions (kg CO₂)",
          data: values,
          borderColor: "#4CAF50",
          fill: false,
          tension: 0.3
        }]
      },
      options: {
        plugins: {
          title: {
            display: true,
            text: "Your Carbon Emission Over Time"
          }
        },
        scales: {
          y: {
            beginAtZero: true
          }
        }
      }
    });
  }
});
