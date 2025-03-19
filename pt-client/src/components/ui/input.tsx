import * as React from "react";

import { cva } from "class-variance-authority";
import { cn } from "@/lib/utils";

export const inputVariants = cva(
  "placeholder:text-muted-foreground selection:bg-primary selection:text-primary-foreground bg-transparent flex h-9 w-full min-w-0 px-3 py-1 text-base outline-none disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50 md:text-sm font-normal",
  {
    variants: {
      variant: {
        default: [
          "file:text-foreground dark:bg-input/30 border-input rounded-md border shadow-xs transition-[color,box-shadow] file:inline-flex file:h-7 file:border-0 file:bg-transparent file:text-sm file:font-medium",
          "focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px]",
          "aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive",
        ],
        ghost: "",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
);

function Input({
  className,
  type,
  variant = "default",
  ...props
}: React.ComponentProps<"input"> & { variant?: "default" | "ghost" }) {
  return (
    <input
      type={type}
      data-slot="input"
      className={cn(inputVariants({ variant, className }))}
      {...props}
    />
  );
}

export function InputWrapper({
  className,
  children,
  ...props
}: React.ComponentProps<"div">) {
  return (
    <div
      className={cn(
        "file:text-foreground placeholder:text-muted-foreground selection:bg-primary selection:text-primary-foreground dark:bg-input/30 border-input flex w-full min-w-0 rounded-md border bg-transparent px-3 py-1 text-base shadow-xs transition-[color,box-shadow] outline-none file:inline-flex file:h-7 file:border-0 file:bg-transparent file:text-sm file:font-medium disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50 md:text-sm font-normal",
        "focus-within:border-ring focus-within:ring-ring/50 focus-within:ring-[3px]",
        "has-[aria-invalid]:ring-destructive/20 dark:has-[aria-invalid]:ring-destructive/40 has-[aria-invalid]:border-destructive",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}

export { Input };
