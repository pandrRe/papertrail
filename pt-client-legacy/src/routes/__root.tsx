import { Outlet, createRootRoute } from "@tanstack/react-router";
import { TanStackRouterDevtools } from "@tanstack/react-router-devtools";

// import Header from "../components/Header";

export const Route = createRootRoute({
  component: () => (
    <div className="bg-background text-foreground text-sm">
      {/* <Header /> */}

      <Outlet />
      <TanStackRouterDevtools />
    </div>
  ),
});
