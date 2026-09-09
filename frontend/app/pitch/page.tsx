import PitchForm from '../../components/PitchForm';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';

export default function PitchPage() {
  return (
    <div className="py-12 px-4 sm:px-6 max-w-6xl mx-auto w-full">
      <div className="mb-6 text-left">
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-sm text-slate-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Overview</span>
        </Link>
      </div>

      <PitchForm />
    </div>
  );
}
