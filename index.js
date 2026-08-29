require("dotenv").config();

const { App } = require("@slack/bolt");
const axios = require("axios");

const app = new App({
  token: process.env.SLACK_BOT_TOKEN,
  appToken: process.env.SLACK_APP_TOKEN,
  socketMode: true,
});

// Basic ping
app.command("/bot-ping", async ({ command, ack, respond }) => {
  const start = Date.now();
  await ack();
  const latency = Date.now() - start;
  await respond({ text: `Pong!\nLatency: ${latency}ms` });
});

// Joke command using external API
app.command("/bot-joke", async ({ command, ack, respond }) => {
  await ack();
  try {
    const response = await axios.get("https://official-joke-api.appspot.com/random_joke");
    await respond({
      text: `${response.data.setup}\n\n${response.data.punchline}`,
    });
  } catch (err) {
    await respond({ text: "Failed to fetch a joke." });
  }
});

// School-related helper commands
app.command("/bot-office-hours", async ({ ack, respond }) => {
  await ack();
  await respond({ text: "The school office is open from 8:00 AM to 3:00 PM." });
});

app.command("/bot-uniform", async ({ ack, respond }) => {
  await ack();
  await respond({ text: "Students are expected to wear the school uniform every day. Refer to the handbook for details." });
});

app.command("/bot-admission", async ({ ack, respond }) => {
  await ack();
  await respond({ text: "Admissions are handled through the school office. Visit the admissions desk or call the office for application information." });
});

app.command("/bot-contact", async ({ ack, respond }) => {
  await ack();
  await respond({ text: "School Office: +1-555-151-0041\nEmail: office@school.edu" });
});

app.command("/bot-calendar", async ({ ack, respond }) => {
  await ack();
  await respond({ text: "Upcoming events:\n- Sep 1: First day of term\n- Oct 15: Parent-teacher conference\n- Dec 20: Winter break begins" });
});

app.command("/bot-lunch", async ({ ack, respond }) => {
  await ack();
  await respond({ text: "Today's lunch: Grilled chicken, steamed vegetables, rice, and fruit." });
});

app.command("/bot-directions", async ({ ack, respond }) => {
  await ack();
  await respond({ text: "The school is located at 123 Main St. Parking available at the north lot. Use the Oak Ave entrance." });
});

app.command("/bot-staff", async ({ ack, respond }) => {
  await ack();
  await respond({ text: "Principal: Dr. Smith\nVice Principal: Ms. Johnson\nFront office: +1-555-151-0041" });
});

app.command("/bot-holidays", async ({ ack, respond }) => {
  await ack();
  await respond({ text: "School holidays:\n- Thanksgiving Break: Nov 24-26\n- Winter Break: Dec 20 - Jan 3" });
});

app.command("/bot-help", async ({ ack, respond }) => {
  await ack();
  await respond({
    text:
      "Available commands:\n" +
      "/bot-ping, /bot-joke, /bot-office-hours, /bot-uniform, /bot-admission,\n" +
      "/bot-contact, /bot-calendar, /bot-lunch, /bot-directions, /bot-staff, /bot-holidays, /bot-help",
  });
});

(async () => {
  await app.start();
  console.log("bot is running!");
})();
