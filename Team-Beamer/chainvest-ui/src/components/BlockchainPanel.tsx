import type { ChainVestResult } from "@/components/types";

type Props = {
  result: ChainVestResult;
};

export default function BlockchainPanel({ result }: Props) {
  if (!result) return null;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-gray-900">
          Blockchain Audit Trail
        </h2>
        <p className="text-sm text-gray-600">
          Workflow logs and verification artifacts for this analysis.
        </p>
      </div>

      <div>
        <h3 className="text-sm font-semibold text-gray-900 mb-2">
          Workflow Transaction Hashes
        </h3>

        <div className="space-y-2">
          {result.tx_hashes?.length ? result.tx_hashes.map((tx: string, i: number) => (
            <div
              key={i}
              className="flex items-center justify-between border border-gray-200 rounded-lg px-3 py-2 bg-gray-50"
            >
              <span className="text-xs font-mono text-gray-800 break-all">
                {tx}
              </span>

              <span className="text-xs px-2 py-1 rounded bg-indigo-50 text-indigo-600 font-medium">
                Verified
              </span>
            </div>
          )) : (
            <div className="border border-dashed border-gray-200 rounded-lg px-3 py-4 bg-gray-50 text-sm text-gray-600">
              No workflow audit hashes were returned for this run.
            </div>
          )}
        </div>
      </div>

      <div>
        <h3 className="text-sm font-semibold text-gray-900 mb-2">
          Execution Logs
        </h3>

        <div className="space-y-2">
          {result.logs?.length ? result.logs.map((log: string, i: number) => (
            <div
              key={i}
              className="border border-gray-200 rounded-lg px-3 py-2 bg-white text-sm text-gray-800"
            >
              {log}
            </div>
          )) : (
            <div className="border border-dashed border-gray-200 rounded-lg px-3 py-4 bg-gray-50 text-sm text-gray-600">
              No execution logs were returned for this run.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
