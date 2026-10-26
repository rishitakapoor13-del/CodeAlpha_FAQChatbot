// Chat page for Willow, the FAQ assistant (CodeAlpha AI Internship, Task 2)
const messagesEl = document.getElementById("messages");
const inputEl = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");
const chipsEl = document.getElementById("chips");
const catsEl = document.getElementById("cats");

const STARTERS = [
  "Where is my order?",
  "How long does delivery take?",
  "What is your return policy?",
  "How do I create an account?"
];
const ARROW = '<svg viewBox="0 0 24 24"><path d="M7 17L17 7M8 7h9v9"/></svg>';

function scrollDown() {
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function addMessage(text, who) {
  const div = document.createElement("div");
  div.className = "msg " + who;
  div.textContent = text;
  messagesEl.appendChild(div);
  scrollDown();
  return div;
}

function addQuestionList(parent, questions) {
  const list = document.createElement("div");
  list.className = "qlist";
  questions.forEach((q) => {
    const b = document.createElement("button");
    b.type = "button";
    b.className = "qbtn";
    b.textContent = q;
    b.addEventListener("click", () => sendMessage(q));
    list.appendChild(b);
  });
  parent.appendChild(list);
}

function showBotReply(data) {
  const div = addMessage(data.answer, "bot");
  if (data.matched_question) {
    const meta = document.createElement("span");
    meta.className = "meta";
    meta.textContent = "Matched FAQ: " + data.matched_question + "  |  " + Math.round(data.score * 100) + "% match";
    div.appendChild(meta);
  }
  if (data.suggestions && data.suggestions.length) addQuestionList(div, data.suggestions);
  scrollDown();
}

async function sendMessage(text) {
  text = (text || inputEl.value).trim();
  if (!text) return;
  addMessage(text, "user");
  inputEl.value = "";
  sendBtn.disabled = true;

  const typing = document.createElement("div");
  typing.className = "msg bot typing";
  typing.innerHTML = "<span></span><span></span><span></span>";
  messagesEl.appendChild(typing);
  scrollDown();

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text })
    });
    const data = await response.json();
    typing.remove();
    if (!response.ok) addMessage(data.error || "Something went wrong.", "bot");
    else showBotReply(data);
  } catch (err) {
    typing.remove();
    addMessage("I cannot reach the server. Make sure app.py is running.", "bot");
  } finally {
    sendBtn.disabled = false;
    inputEl.focus();
  }
}

function showTopic(category) {
  const div = addMessage("Here are some common questions about " + category.name.toLowerCase() + ". Tap one, or type your own.", "bot");
  addQuestionList(div, category.questions);
  scrollDown();
}

function start() {
  messagesEl.textContent = "";
  addMessage("Hi, I am Willow. Ask me anything about orders, shipping, returns or getting started, or pick a topic on the left.", "bot");
}

async function loadTopics() {
  try {
    const res = await fetch("/api/categories");
    const categories = await res.json();
    categories.forEach((category) => {
      const b = document.createElement("button");
      b.type = "button";
      b.className = "cat";
      const label = document.createElement("span");
      label.textContent = category.name;
      b.appendChild(label);
      b.insertAdjacentHTML("beforeend", ARROW);
      b.addEventListener("click", () => {
        showTopic(category);
        if (window.innerWidth <= 900) document.querySelector(".chat").scrollIntoView({ behavior: "smooth" });
      });
      catsEl.appendChild(b);
    });
  } catch (err) {
    /* the server is not running; the chat will explain it */
  }
}

STARTERS.forEach((q) => {
  const chip = document.createElement("button");
  chip.type = "button";
  chip.className = "chip";
  chip.textContent = q;
  chip.addEventListener("click", () => sendMessage(q));
  chipsEl.appendChild(chip);
});

sendBtn.addEventListener("click", () => sendMessage());
inputEl.addEventListener("keydown", (e) => { if (e.key === "Enter") sendMessage(); });
document.getElementById("resetBtn").addEventListener("click", () => { start(); inputEl.focus(); });

start();
loadTopics();
