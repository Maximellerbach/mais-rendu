import { createRootRoute, Outlet } from "@tanstack/react-router";
import { FloatingNav } from "../components/navbar";

export const Route = createRootRoute({
    component: () => (
        <>
            <FloatingNav
                navItems={[
                    {
                        name: "Home",
                        link: "/",
                    },
                    {
                        name: "Demo",
                        link: "/demo",
                    },
                ]}
            />
            <Outlet />
        </>
    ),
});
