import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { Slot } from "@radix-ui/react-slot";

import { cn } from "@/lib/utils";

const inputVariants = cva(
  "file:text-foreground placeholder:text-muted-foreground selection:bg-primary selection:text-primary-foreground dark:bg-background flex h-9 w-full min-w-0 rounded-md bg-transparent px-3 py-1 text-base shadow-xs transition-[color,box-shadow] outline-none file:inline-flex file:h-7 file:border-0 file:bg-transparent file:text-sm file:font-medium disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50 md:text-sm aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive",
  {
    variants: {
      variant: {
        default:
          "border border-input focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px]",
        ghost: "border-0 focus-visible:border-0 focus-visible:ring-0",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
);

export interface InputProps
  extends React.ComponentProps<"input">,
    VariantProps<typeof inputVariants> {}

function Input({ className, type, variant, ...props }: InputProps) {
  return (
    <input
      type={type}
      data-slot="input"
      className={cn(inputVariants({ variant, className }))}
      {...props}
    />
  );
}

const inputLayoutVariants = cva(
  "border border-input rounded-md bg-transparent transition-[color,box-shadow] focus-within:border-ring focus-within:ring-ring/50 focus-within:ring-[3px]"
);

export interface InputLayoutProps extends React.ComponentProps<"div"> {
  asChild?: boolean;
}

function InputLayout({
  className,
  asChild = false,
  role = "textbox",
  ...props
}: InputLayoutProps) {
  const Comp = asChild ? Slot : "div";

  return (
    <Comp
      role={role}
      className={cn(inputLayoutVariants(), className)}
      {...props}
    />
  );
}

export { Input, InputLayout };
