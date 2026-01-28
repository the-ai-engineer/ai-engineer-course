"use client";

import { useEffect, useRef, useState } from "react";
import { Send, HelpCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import ChatMessage from "@/components/ChatMessage";
import { ChatError, Message, Source, streamChat } from "@/lib/api";

const EXAMPLE_QUESTIONS = [
  "How do I return an item?",
  "What payment methods do you accept?",
  "Do you ship internationally?",
  "How do I track my order?",
];

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (overrideContent?: string) => {
    const content = (overrideContent ?? input).trim();
    if (!content || isLoading) return;

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content,
    };

    const assistantMessage: Message = {
      id: crypto.randomUUID(),
      role: "assistant",
      content: "",
    };

    setMessages((prev) => [...prev, userMessage, assistantMessage]);
    setInput("");
    setIsLoading(true);

    try {
      await streamChat(
        content,
        (token) => {
          setMessages((prev) => {
            const lastIndex = prev.length - 1;
            const lastMsg = prev[lastIndex];
            if (lastMsg.role === "assistant") {
              return [
                ...prev.slice(0, lastIndex),
                { ...lastMsg, content: lastMsg.content + token },
              ];
            }
            return prev;
          });
        },
        (sources?: Source[]) => {
          if (sources) {
            setMessages((prev) => {
              const lastIndex = prev.length - 1;
              const lastMsg = prev[lastIndex];
              if (lastMsg.role === "assistant") {
                return [
                  ...prev.slice(0, lastIndex),
                  { ...lastMsg, sources },
                ];
              }
              return prev;
            });
          }
          setIsLoading(false);
        }
      );
    } catch (error) {
      console.error("Failed to send message:", error);
      setIsLoading(false);
      const errorMessage =
        error instanceof ChatError
          ? error.message
          : "Sorry, an error occurred. Please try again.";
      setMessages((prev) => {
        const updated = [...prev];
        const lastMsg = updated[updated.length - 1];
        if (lastMsg.role === "assistant") {
          lastMsg.content = `Error: ${errorMessage}`;
          lastMsg.error = errorMessage;
        }
        return updated;
      });
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-screen bg-background">
      {/* Header */}
      <header className="bg-zinc-50 border-b border-zinc-200 px-6 py-5">
        <h1 className="text-xl font-semibold text-zinc-900">Customer Support</h1>
        <p className="text-sm text-zinc-500">
          Ask questions about our product
        </p>
      </header>

      {/* Messages */}
      <ScrollArea className="flex-1">
        <div className="max-w-3xl mx-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <div className="space-y-6">
              <Card className="p-8 text-center">
                <HelpCircle className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                <h2 className="text-lg font-medium mb-2">
                  How can I help you today?
                </h2>
                <p className="text-muted-foreground">
                  Ask me anything about our products, orders, shipping, or
                  returns. I'll search our knowledge base to find the answer.
                </p>
              </Card>

              <div className="space-y-3">
                <p className="text-sm text-muted-foreground text-center">
                  Try asking:
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {EXAMPLE_QUESTIONS.map((question) => (
                    <Button
                      key={question}
                      variant="outline"
                      className="h-auto py-3 px-4 text-left justify-start text-sm whitespace-normal"
                      onClick={() => handleSend(question)}
                    >
                      {question}
                    </Button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            messages.map((message, index) => (
              <ChatMessage
                key={message.id}
                message={message}
                isLoading={isLoading && index === messages.length - 1}
              />
            ))
          )}
          <div ref={scrollRef} />
        </div>
      </ScrollArea>

      {/* Input */}
      <div className="border-t px-4 py-6 bg-background">
        <div className="max-w-3xl mx-auto flex gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question..."
            disabled={isLoading}
            rows={1}
            className="flex-1 resize-none rounded-lg border border-input bg-background px-4 py-3 focus:outline-none focus:ring-2 focus:ring-ring disabled:opacity-50"
          />
          <Button
            onClick={() => handleSend()}
            disabled={isLoading || !input.trim()}
            className="px-4 py-3 h-auto"
            aria-label="Send message"
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
