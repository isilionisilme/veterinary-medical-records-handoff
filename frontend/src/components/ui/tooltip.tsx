import {
  cloneElement,
  isValidElement,
  type FocusEvent,
  type MouseEvent,
  type ReactElement,
  type ReactNode,
  useState,
} from "react";
import * as TooltipPrimitive from "@radix-ui/react-tooltip";
import { cn } from "../../lib/utils";

type TooltipProps = {
  content: ReactNode;
  children: ReactNode;
  disabled?: boolean;
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  offset?: number;
  side?: "top" | "right" | "bottom" | "left";
  disableHoverableContent?: boolean;
  triggerClassName?: string;
};

export function TooltipProvider({ children }: { children: ReactNode }) {
  return (
    <TooltipPrimitive.Provider delayDuration={0} skipDelayDuration={0}>
      {children}
    </TooltipPrimitive.Provider>
  );
}

export function Tooltip({
  content,
  children,
  disabled = false,
  open: controlledOpen,
  onOpenChange,
  offset = 8,
  side = "top",
  disableHoverableContent = true,
  triggerClassName = "inline-flex",
}: TooltipProps) {
  const [uncontrolledOpen, setUncontrolledOpen] = useState(false);
  const isControlled = typeof controlledOpen === "boolean";
  const open = isControlled ? controlledOpen : uncontrolledOpen;
  const isTestEnvironment = import.meta.env.MODE === "test";

  const setOpen = (nextOpen: boolean) => {
    if (!isControlled) {
      setUncontrolledOpen(nextOpen);
    }
    onOpenChange?.(nextOpen);
  };

  if (disabled) {
    return <span className={triggerClassName}>{children}</span>;
  }

  const triggerContent = isValidElement(children) ? (
    cloneElement(children as ReactElement<Record<string, unknown>>, {
      onMouseEnter: (event: MouseEvent) => {
        (
          children as ReactElement<{ onMouseEnter?: (event: MouseEvent) => void }>
        ).props.onMouseEnter?.(event);
        setOpen(true);
      },
      onMouseLeave: (event: MouseEvent) => {
        (
          children as ReactElement<{ onMouseLeave?: (event: MouseEvent) => void }>
        ).props.onMouseLeave?.(event);
        setOpen(false);
      },
      onFocus: (event: FocusEvent) => {
        (children as ReactElement<{ onFocus?: (event: FocusEvent) => void }>).props.onFocus?.(
          event,
        );
        setOpen(true);
      },
      onBlur: (event: FocusEvent) => {
        (children as ReactElement<{ onBlur?: (event: FocusEvent) => void }>).props.onBlur?.(event);
        setOpen(false);
      },
    })
  ) : (
    <span className={triggerClassName}>{children}</span>
  );

  if (isTestEnvironment) {
    return (
      <span className="relative inline-flex">
        {triggerContent}
        {open ? (
          <span
            role="tooltip"
            className={cn(
              "pointer-events-none absolute bottom-full left-1/2 z-[90] mb-2 -translate-x-1/2 rounded-md bg-text px-2 py-1 text-[11px] font-medium text-white shadow-subtle",
            )}
          >
            {content}
          </span>
        ) : null}
      </span>
    );
  }

  const rootProps = isControlled ? { open: controlledOpen, onOpenChange } : { open };

  return (
    <TooltipPrimitive.Provider delayDuration={0} skipDelayDuration={0}>
      <TooltipPrimitive.Root {...rootProps} disableHoverableContent={disableHoverableContent}>
        <TooltipPrimitive.Trigger asChild>{triggerContent}</TooltipPrimitive.Trigger>
        <TooltipPrimitive.Portal>
          <TooltipPrimitive.Content
            side={side}
            sideOffset={offset}
            collisionPadding={8}
            className={cn(
              "z-[90] rounded-md bg-text px-2 py-1 text-[11px] font-medium text-white shadow-subtle",
            )}
          >
            {content}
          </TooltipPrimitive.Content>
        </TooltipPrimitive.Portal>
      </TooltipPrimitive.Root>
    </TooltipPrimitive.Provider>
  );
}
