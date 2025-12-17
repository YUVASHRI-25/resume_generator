import ResumeBuilderLayout from './ResumeBuilderLayout'

const Summary = () => {
  return (
    <ResumeBuilderLayout>
      <h1 className="text-2xl font-bold text-gray-900 mb-2">Summary</h1>
      <p className="text-gray-600 mb-6">
        Write a short professional summary that highlights your strengths.
      </p>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Professional summary
        </label>
        <textarea
          rows={5}
          className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Motivated developer with a passion for building scalable web applications..."
        />
      </div>
    </ResumeBuilderLayout>
  )
}

export default Summary


