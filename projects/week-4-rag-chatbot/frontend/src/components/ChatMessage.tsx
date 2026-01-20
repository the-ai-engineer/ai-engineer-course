"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { User, Bot } from "lucide-react";
import { cn } from "@/lib/utils";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import type { Message } from "@/lib/api";
import Sources from "./Sources";

interface ChatMessageProps {
  message: Message;
  isLoading?: boolean;
}

function LoadingDots() {
  return (
    <div className="flex items-center gap-1">
      <span className="animate-bounce h-2 w-2 rounded-full bg-current" />
      <span className="animate-bounce h-2 w-2 rounded-full bg-current [animation-delay:150ms]" />
      <span className="animate-bounce h-2 w-2 rounded-full bg-current [animation-delay:300ms]" />
    </div>
  );
}

export default function ChatMessage({ message, isLoading }: ChatMessageProps) {
  const isUser = message.role === "user";
  const showLoading = isLoading && !isUser && !message.content;

  return (
    <div
      className={cn(
        "flex items-start gap-3",
        isUser ? "flex-row-reverse" : "flex-row"
      )}
    >
      <Avatar
        className={cn(
          "mt-0.5",
          isUser ? "bg-primary" : "bg-secondary border border-border"
        )}
      >
        <AvatarFallback>
          {isUser ? (
            <User className="h-4 w-4 text-primary-foreground" />
          ) : (
            <Bot className="h-4 w-4 text-secondary-foreground" />
          )}
        </AvatarFallback>
      </Avatar>

      <div
        className={cn(
          "max-w-[85%] rounded-lg px-4 py-3",
          isUser
            ? "bg-primary text-primary-foreground"
            : "bg-secondary text-secondary-foreground"
        )}
      >
        {isUser ? (
          <p className="whitespace-pre-wrap text-sm">{message.content}</p>
        ) : showLoading ? (
          <LoadingDots />
        ) : (
          <div className="prose prose-sm max-w-none dark:prose-invert text-sm [&>p]:my-1">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {message.content || "Thinking..."}
            </ReactMarkdown>
          </div>
        )}
        {!isUser && message.sources && message.sources.length > 0 && (
          <Sources sources={message.sources} />
        )}
      </div>
    </div>
  );
}
