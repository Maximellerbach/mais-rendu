"use client";

import React, {
    createContext,
    useState,
    useContext,
    useRef,
    useEffect,
} from "react";
import { cn } from "../utils/cn";
import { Link } from "@tanstack/react-router";

import MessiImg from "../assets/messi.png";

const MouseEnterContext = createContext<
    [boolean, React.Dispatch<React.SetStateAction<boolean>>] | undefined
>(undefined);

export const CardContainer = ({
    children,
    className,
    containerClassName,
}: {
    children?: React.ReactNode;
    className?: string;
    containerClassName?: string;
}) => {
    const containerRef = useRef<HTMLDivElement>(null);
    const [isMouseEntered, setIsMouseEntered] = useState(false);

    const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
        if (!containerRef.current) return;
        const { left, top, width, height } =
            containerRef.current.getBoundingClientRect();
        const x = (e.clientX - left - width / 2) / 25;
        const y = (e.clientY - top - height / 2) / 25;
        containerRef.current.style.transform = `rotateY(${x}deg) rotateX(${y}deg)`;
    };

    const handleMouseEnter = (e: React.MouseEvent<HTMLDivElement>) => {
        setIsMouseEntered(true);
        if (!containerRef.current) return;
    };

    const handleMouseLeave = (e: React.MouseEvent<HTMLDivElement>) => {
        if (!containerRef.current) return;
        setIsMouseEntered(false);
        containerRef.current.style.transform = `rotateY(0deg) rotateX(0deg)`;
    };
    return (
        <MouseEnterContext.Provider value={[isMouseEntered, setIsMouseEntered]}>
            <div
                className={cn(
                    "py-20 flex items-center justify-center",
                    containerClassName
                )}
                style={{
                    perspective: "1000px",
                }}
            >
                <div
                    ref={containerRef}
                    onMouseEnter={handleMouseEnter}
                    onMouseMove={handleMouseMove}
                    onMouseLeave={handleMouseLeave}
                    className={cn(
                        "flex items-center justify-center relative transition-all duration-200 ease-linear",
                        className
                    )}
                    style={{
                        transformStyle: "preserve-3d",
                    }}
                >
                    {children}
                </div>
            </div>
        </MouseEnterContext.Provider>
    );
};

export const CardBody = ({
    children,
    className,
}: {
    children: React.ReactNode;
    className?: string;
}) => {
    return (
        <div
            className={cn(
                "h-96 w-96 [transform-style:preserve-3d]  [&>*]:[transform-style:preserve-3d]",
                className
            )}
        >
            {children}
        </div>
    );
};

export const CardItem = ({
    as: Tag = "div",
    children,
    className,
    translateX = 0,
    translateY = 0,
    translateZ = 0,
    rotateX = 0,
    rotateY = 0,
    rotateZ = 0,
    ...rest
}: {
    as?: React.ElementType;
    children: React.ReactNode;
    className?: string;
    translateX?: number | string;
    translateY?: number | string;
    translateZ?: number | string;
    rotateX?: number | string;
    rotateY?: number | string;
    rotateZ?: number | string;
    [key: string]: any;
}) => {
    const ref = useRef<HTMLDivElement>(null);
    const [isMouseEntered] = useMouseEnter();

    useEffect(() => {
        handleAnimations();
    }, [isMouseEntered]);

    const handleAnimations = () => {
        if (!ref.current) return;
        if (isMouseEntered) {
            ref.current.style.transform = `translateX(${translateX}px) translateY(${translateY}px) translateZ(${translateZ}px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) rotateZ(${rotateZ}deg)`;
        } else {
            ref.current.style.transform = `translateX(0px) translateY(0px) translateZ(0px) rotateX(0deg) rotateY(0deg) rotateZ(0deg)`;
        }
    };

    return (
        <Tag
            ref={ref}
            className={cn(
                "w-fit transition duration-200 ease-linear",
                className
            )}
            {...rest}
        >
            {children}
        </Tag>
    );
};

// Create a hook to use the context
export const useMouseEnter = () => {
    const context = useContext(MouseEnterContext);
    if (context === undefined) {
        throw new Error(
            "useMouseEnter must be used within a MouseEnterProvider"
        );
    }
    return context;
};

export function Card() {
    return (
        <CardContainer className="inter-var cursor-pointer">
            <CardBody className="bg-gray-50 relative group/card  dark:hover:shadow-2xl dark:hover:shadow-emerald-500/[0.1] dark:bg-black dark:border-white/[0.2] border-black/[0.1] w-auto sm:w-[30rem] h-auto rounded-xl p-6 border  ">
                <CardItem
                    translateZ="50"
                    className="text-xl font-bold text-neutral-600 dark:text-white"
                >
                    Enabling new perspectives
                </CardItem>
                <CardItem
                    as="p"
                    translateZ="60"
                    className="text-neutral-500 text-sm max-w-sm mt-2 dark:text-neutral-300"
                >
                    Experience the game like never before with our immersive
                    simulation
                </CardItem>
                <CardItem translateZ="100" className="w-full mt-4">
                    <Link to="/demo">
                        <img
                            src={MessiImg}
                            alt="Messi"
                            className=" w-full object-cover rounded-xl group-hover/card:shadow-xl"
                        />
                    </Link>
                </CardItem>
                <div className="flex justify-between items-center mt-20">
                    <CardItem
                        translateZ={20}
                        as={Link}
                        href="https://twitter.com/mannupaaji"
                        target="__blank"
                        className="px-4 py-2 rounded-xl text-xs font-normal dark:text-white"
                    >
                        Try now →
                    </CardItem>
                </div>
            </CardBody>
        </CardContainer>
    );
}
