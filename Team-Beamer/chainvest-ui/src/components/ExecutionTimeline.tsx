type Props = {
  result: any;
};

export default function ExecutionTimeline({ result }: Props) {
  if (!result || !result.logs) return null;

  return (
    <div className="p-6 border rounded-lg bg-white shadow space-y-4">

      <h2 className="text-xl font-bold">Execution Timeline</h2>

      <ul className="space-y-2">
        {result.logs.map((log: string, i: number) => (
          <li
            key={i}
            className="p-3 border rounded bg-gray-50 text-sm"
          >
            {log}
          </li>
        ))}
      </ul>

    </div>
  );
}