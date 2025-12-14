"use client";

import { useState, useEffect } from "react";
import { MessageCircle, X, Send, User } from "lucide-react";

interface Message {
  role: string;
  content: string;
  timestamp: string;
}

export function ChatWidget() {
  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const [isOpen, setIsOpen] = useState(false);
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [sessionId, setSessionId] = useState("default-session");
  const [token, setToken] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [connectionError, setConnectionError] = useState("");

  useEffect(() => {
    const t = localStorage.getItem("token");
    setToken(t ?? "");
    if (t && isOpen) {
      fetch(`${API_URL}/api/v1/chat/conversations`, {
        headers: { Authorization: `Bearer ${t}` },
      })
        .then((res) => res.json())
        .then((data) => {
          if (data.length > 0) {
            const sid = data[0].session_id;
            setSessionId(sid);
            loadMessages(sid, t);
          }
        });
    }
  }, [isOpen, token]);

  const loadMessages = (sid: string, t: string) => {
    fetch(`${API_URL}/api/v1/chat/conversations/${sid}/messages`, {
      headers: { Authorization: `Bearer ${t}` },
    })
      .then((res) => res.json())
      .then((data) => setMessages(data));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && token) {
      // Show typing indicator
      setIsTyping(true);
      setConnectionError("");

      fetch(`${API_URL}/api/v1/chat/messages`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          session_id: sessionId,
          content: message,
          role: "user",
        }),
      })
        .then((res) => {
          if (!res.ok) {
            throw new Error(`HTTP error! status: ${res.status}`);
          }
          return res.json();
        })
        .then((data) => {
          setMessages([
            ...messages,
            {
              role: "user",
              content: message,
              timestamp: data.user_message.timestamp,
            },
            {
              role: "assistant",
              content: data.bot_message.content,
              timestamp: data.bot_message.timestamp,
            },
          ]);
          setMessage("");
          setIsTyping(false);
        })
        .catch((error) => {
          console.error("Error sending message:", error);
          setConnectionError("Connection error. Please try again.");
          setIsTyping(false);
          setMessages([
            ...messages,
            {
              role: "user",
              content: message,
              timestamp: new Date().toISOString(),
            },
            {
              role: "assistant",
              content:
                "Sorry, I couldn't process your message. Please try again.",
              timestamp: new Date().toISOString(),
            },
          ]);
          setMessage("");
        });
    }
  };

  return (
    <>
      {/* Chat Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-8 right-8 z-50 p-4 rounded-full bg-primary-600 text-white shadow-lg hover:bg-primary-700 transition-all duration-300 hover:scale-110 flex items-center gap-2"
          aria-label="Open chat"
        >
          <MessageCircle className="w-6 h-6" />
          <span className="hidden sm:inline text-sm font-semibold">
            Chat with us
          </span>
        </button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div className="fixed bottom-8 right-8 z-50 w-96 max-w-[calc(100vw-2rem)] h-[500px] bg-white rounded-2xl shadow-2xl flex flex-col overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-primary-600 to-primary-700 p-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center">
                <MessageCircle className="w-5 h-5 text-white" />
              </div>
              <div>
                <h3 className="text-white font-semibold">Chat with AI</h3>
                <p className="text-white/80 text-xs">AI-powered assistance</p>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="text-white/80 hover:text-white transition-colors"
              aria-label="Close chat"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 p-4 overflow-y-auto bg-gray-50">
            <div className="space-y-4">
              {messages.length === 0 ? (
                <div className="flex gap-2">
                  <div className="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center flex-shrink-0">
                    <MessageCircle className="w-4 h-4 text-primary-600" />
                  </div>
                  <div className="bg-white rounded-lg rounded-tl-none p-3 shadow-sm max-w-[80%]">
                    <p className="text-sm text-gray-800">
                      Hi! 👋 Welcome to Lean AI Construction. How can we help
                      you today?
                    </p>
                    <p className="text-xs text-gray-500 mt-1">Just now</p>
                  </div>
                </div>
              ) : (
                messages.map((msg, i) => (
                  <div
                    key={i}
                    className={`flex gap-2 ${
                      msg.role === "user" ? "justify-end" : "justify-start"
                    }`}
                  >
                    {msg.role === "bot" && (
                      <div className="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center flex-shrink-0">
                        <MessageCircle className="w-4 h-4 text-primary-600" />
                      </div>
                    )}
                    <div
                      className={`rounded-lg p-3 shadow-sm max-w-[80%] ${
                        msg.role === "user"
                          ? "bg-primary-600 text-white rounded-br-none"
                          : "bg-white rounded-tl-none"
                      }`}
                    >
                      <p className="text-sm">{msg.content}</p>
                      <p
                        className={`text-xs mt-1 ${
                          msg.role === "user"
                            ? "text-primary-100"
                            : "text-gray-500"
                        }`}
                      >
                        {new Date(msg.timestamp).toLocaleTimeString()}
                      </p>
                    </div>
                    {msg.role === "user" && (
                      <div className="w-8 h-8 rounded-full bg-primary-600 flex items-center justify-center flex-shrink-0">
                        <User className="w-4 h-4 text-white" />
                      </div>
                    )}
                  </div>
                ))
              )}

              {/* Typing Indicator */}
              {isTyping && (
                <div className="flex gap-2 justify-start">
                  <div className="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center flex-shrink-0">
                    <MessageCircle className="w-4 h-4 text-primary-600" />
                  </div>
                  <div className="bg-white rounded-lg rounded-tl-none p-3 shadow-sm max-w-[80%]">
                    <div className="flex gap-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div
                        className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                        style={{ animationDelay: "0.1s" }}
                      ></div>
                      <div
                        className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                        style={{ animationDelay: "0.2s" }}
                      ></div>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                      AI is typing...
                    </p>
                  </div>
                </div>
              )}

              {/* Connection Error */}
              {connectionError && (
                <div className="text-center p-2">
                  <p className="text-red-500 text-sm">{connectionError}</p>
                </div>
              )}
            </div>
          </div>

          {/* Input */}
          <form onSubmit={handleSubmit} className="p-4 border-t bg-white">
            <div className="flex gap-2">
              <input
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Type your message..."
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
              <button
                type="submit"
                className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors flex items-center gap-2"
              >
                <Send className="w-4 h-4" />
                <span className="hidden sm:inline">Send</span>
              </button>
            </div>
          </form>
        </div>
      )}
    </>
  );
}
