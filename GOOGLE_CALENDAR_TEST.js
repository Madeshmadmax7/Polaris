async function testGoogleCalendarStatus() {
  try {
    console.log("Testing GET /api/integrations/google-calendar/status...");
    
    const response = await fetch("http://127.0.0.1:8000/api/integrations/google-calendar/status", {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      console.error(`❌ Error: ${response.status} ${response.statusText}`);
      const error = await response.json();
      console.error("Response:", error);
      return;
    }

    const data = await response.json();
    console.log("✅ Success! Response:", data);
    
    // Expected response:
    // {
    //   "connected": false,
    //   "message": "Google Calendar status working",
    //   "status": "ok"
    // }
    
    return data;
    
  } catch (error) {
    console.error("❌ Fetch error:", error.message);
    console.error("Make sure backend is running on http://127.0.0.1:8000");
  }
}

// Call this from useEffect or button click
export function GoogleCalendarTest() {
  return (
    <button onClick={testGoogleCalendarStatus}>
      Test Google Calendar Status
    </button>
  );
}
