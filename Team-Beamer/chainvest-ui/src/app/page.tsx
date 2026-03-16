"use client";

import { useState, type ReactNode } from "react";

import InputForm from "@/components/InputForm";
import RiskDashboard from "@/components/RiskDashboard";
import ExplanationPanel from "@/components/ExplanationPanel";
import BlockchainPanel from "@/components/BlockchainPanel";
import type { ChainVestResult } from "@/components/types";

export default function Home() {
  const [result, setResult] = useState<ChainVestResult | null>(null);

  return (
    <div className="graph-paper-bg min-h-screen">

      {/* NAVBAR */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-6 py-4 flex justify-between items-center">
          <h1 className="brand-wordmark">ChainVest</h1>
          <span className="text-sm text-gray-600">
            Blockchain-Verified AI Decisions
          </span>
        </div>
      </div>

      {/* HERO */}
      <div className="max-w-3xl mx-auto text-center py-16 px-6">
        <h2 className="text-4xl font-semibold text-gray-900 leading-tight">
          AI-Powered Financial Decisions <br /> You Can Trust
        </h2>

        <p className="text-gray-700 mt-4">
          Evaluate startups, loans, and investments with explainable AI and
          blockchain transparency.
        </p>
      </div>

      {/* MAIN */}
      <div className="max-w-5xl mx-auto px-6 pb-20 space-y-6">

        <Card><InputForm onResult={setResult} /></Card>

        {result && (
          <>
            <Card><RiskDashboard result={result} /></Card>
            <Card><BlockchainPanel result={result} /></Card>
            <Card><ExplanationPanel result={result} /></Card>
          </>
        )}

      </div>
    </div>
  );
}

function Card({ children }: { children: ReactNode }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
      {children}
    </div>
  );
}
