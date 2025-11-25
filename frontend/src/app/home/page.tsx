"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

interface Presentation {
  id: string;
  title: string;
  description: string;
  updated_at: string;
  thumbnail_url?: string;
}

export default function HomePage() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [presentations, setPresentations] = useState<Presentation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem("access_token");
    if (!token) {
      router.push("/signin");
      return;
    }

    // Decode JWT to get user info (simple decode, not verification)
    try {
      const payload = JSON.parse(atob(token.split(".")[1]));
      setUser(payload);
    } catch (error) {
      console.error("Invalid token:", error);
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      router.push("/signin");
      return;
    }

    // Fetch user's presentations
    fetchPresentations(token);
  }, [router]);

  const fetchPresentations = async (token: string) => {
    try {
      const response = await fetch(
        "https://gamma-0od0.onrender.com/api/v1/presentations/list",
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setPresentations(data.presentations || []);
      } else {
        console.error("Failed to fetch presentations:", response.statusText);
      }
    } catch (error) {
      console.error("Error fetching presentations:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    router.push("/signin");
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-blue-600">
                Gamma Clone
              </h1>
              {user && (
                <div className="flex items-center space-x-2">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-r from-purple-600 to-blue-600 flex items-center justify-center text-white font-semibold">
                    {user.email?.[0]?.toUpperCase() || "U"}
                  </div>
                  <span className="text-sm text-gray-700">{user.email}</span>
                </div>
              )}
            </div>
            <button
              onClick={handleLogout}
              className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Welcome Section */}
        <div className="mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            Welcome back{user?.email ? `, ${user.email.split("@")[0]}` : ""}!
          </h2>
          <p className="text-gray-600">
            Create beautiful presentations powered by AI
          </p>
        </div>

        {/* Create New Button */}
        <div className="mb-8">
          <Link
            href="/"
            className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white font-medium rounded-lg hover:from-purple-700 hover:to-blue-700 transition-all shadow-lg hover:shadow-xl"
          >
            <svg
              className="w-5 h-5 mr-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 4v16m8-8H4"
              />
            </svg>
            Create New Presentation
          </Link>
        </div>

        {/* Presentations Grid */}
        <div>
          <h3 className="text-xl font-semibold text-gray-900 mb-6">
            Recent Presentations
          </h3>

          {presentations.length === 0 ? (
            <div className="bg-white rounded-lg border-2 border-dashed border-gray-300 p-12 text-center">
              <svg
                className="w-16 h-16 mx-auto text-gray-400 mb-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
              <h4 className="text-lg font-medium text-gray-900 mb-2">
                No presentations yet
              </h4>
              <p className="text-gray-600 mb-6">
                Get started by creating your first AI-powered presentation
              </p>
              <Link
                href="/"
                className="inline-flex items-center px-4 py-2 bg-purple-600 text-white font-medium rounded-lg hover:bg-purple-700 transition-colors"
              >
                Create Presentation
              </Link>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {presentations.map((presentation) => (
                <Link
                  key={presentation.id}
                  href={`/editor/${presentation.id}`}
                  className="group bg-white rounded-lg border border-gray-200 overflow-hidden hover:shadow-lg transition-all"
                >
                  {/* Thumbnail */}
                  <div className="aspect-video bg-gradient-to-br from-purple-100 to-blue-100 flex items-center justify-center">
                    {presentation.thumbnail_url ? (
                      <img
                        src={presentation.thumbnail_url}
                        alt={presentation.title}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <svg
                        className="w-16 h-16 text-purple-400"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                        />
                      </svg>
                    )}
                  </div>

                  {/* Content */}
                  <div className="p-4">
                    <h4 className="font-semibold text-gray-900 mb-1 group-hover:text-purple-600 transition-colors">
                      {presentation.title}
                    </h4>
                    <p className="text-sm text-gray-600 line-clamp-2 mb-3">
                      {presentation.description || "No description"}
                    </p>
                    <p className="text-xs text-gray-500">
                      Updated {new Date(presentation.updated_at).toLocaleDateString()}
                    </p>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
