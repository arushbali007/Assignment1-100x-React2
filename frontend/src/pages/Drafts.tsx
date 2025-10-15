import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Mail as MailIcon,
  Settings,
  Send,
  Plus,
  Loader2,
  FileText,
  Sparkles,
  RefreshCw,
  Trash2,
  Copy,
  Clock,
  Calendar,
  RotateCcw,
  User,
  LogOut,
  HelpCircle,
} from "lucide-react";
import { Link } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { draftsApi, trendsApi, sourcesApi, newsletterSendsApi } from "@/lib/api";
import { toast } from "sonner";

// Helper function to extract and clean HTML content from backend
const extractCleanContent = (htmlString: string) => {
  if (!htmlString) return "";

  // Create a temporary div to parse the HTML
  const tempDiv = document.createElement('div');
  tempDiv.innerHTML = htmlString;

  // Try to find the .container div and extract its content
  const container = tempDiv.querySelector('.container');
  const contentToUse = container || tempDiv.querySelector('body') || tempDiv;

  // Get the innerHTML and remove inline styles that restrict width
  let cleanedHTML = contentToUse.innerHTML;

  // Remove max-width, width constraints from inline styles
  cleanedHTML = cleanedHTML
    .replace(/max-width:\s*\d+px;?/gi, '')
    .replace(/width:\s*\d+px;?/gi, '')
    .replace(/margin:\s*0\s+auto;?/gi, '')
    .replace(/margin-left:\s*auto;?/gi, '')
    .replace(/margin-right:\s*auto;?/gi, '');

  return cleanedHTML;
};

export default function Drafts() {
  const { user, logout } = useAuth();
  const [isLoading, setIsLoading] = useState(true);
  const [drafts, setDrafts] = useState<any[]>([]);
  const [selectedDraft, setSelectedDraft] = useState<any>(null);
  const [trends, setTrends] = useState<any[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [sourceCount, setSourceCount] = useState(0);
  const [isSending, setIsSending] = useState(false);
  const [isRegenerating, setIsRegenerating] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setIsLoading(true);
      const [draftsResponse, trendsResponse, sourcesStats] = await Promise.all([
        draftsApi.getAll(1, 10),
        trendsApi.getTop(5),
        sourcesApi.getStats(),
      ]);

      const draftsList = draftsResponse.drafts || [];
      setDrafts(draftsList);
      setTrends(trendsResponse.trends || []);
      setSourceCount(sourcesStats.total || 0);

      if (draftsList.length > 0) {
        setSelectedDraft(draftsList[0]);
      }
    } catch (error: any) {
      console.error("Failed to load drafts:", error);
      toast.error("Failed to load drafts");
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateDraft = async () => {
    if (sourceCount === 0) {
      toast.error("Please add sources first before generating a draft");
      return;
    }

    setIsGenerating(true);
    try {
      // Always force regenerate to ensure fresh content from all sources
      const newDraft = await draftsApi.generate(true, true, 3);
      toast.success("Draft generated successfully!");
      await loadData();
      setSelectedDraft(newDraft);
    } catch (error: any) {
      console.error("Generate draft error:", error);
      toast.error(error?.message || "Failed to generate draft. Make sure you have sources and content.");
    } finally {
      setIsGenerating(false);
    }
  };

  const handleRegenerateDraft = async () => {
    if (sourceCount === 0) {
      toast.error("Please add sources first before regenerating");
      return;
    }

    const confirmed = confirm("Generate a new version of this newsletter? This will create a fresh draft with different content.");
    if (!confirmed) return;

    setIsRegenerating(true);
    try {
      // Force regenerate with new content
      const newDraft = await draftsApi.generate(true, true, 3);
      toast.success("New draft regenerated successfully!");
      await loadData();
      setSelectedDraft(newDraft);
    } catch (error: any) {
      console.error("Regenerate draft error:", error);
      toast.error(error?.message || "Failed to regenerate draft. Please try again.");
    } finally {
      setIsRegenerating(false);
    }
  };

  const handleSendDraft = async () => {
    if (!selectedDraft) return;

    // Hardcoded recipient email for testing
    const recipientEmail = "arush0704@gmail.com";

    const confirmed = confirm(
      `Send "${selectedDraft.subject}" to ${recipientEmail}?\n\nNote: This will send the newsletter as a test email.`
    );
    if (!confirmed) return;

    setIsSending(true);
    try {
      const result = await newsletterSendsApi.send(
        selectedDraft.id,
        recipientEmail,
        true, // isTest = true
        undefined, // fromEmail - backend will use default
        "CreatorPulse" // fromName
      );

      toast.success(`Newsletter sent successfully to ${recipientEmail}!`);

      // Update the draft status to sent
      await draftsApi.update(selectedDraft.id, { status: "sent" });
      await loadData();
    } catch (error: any) {
      console.error("Send draft error:", error);
      toast.error(error?.message || "Failed to send newsletter. Please check your email configuration.");
    } finally {
      setIsSending(false);
    }
  };

  const handleDeleteDraft = async (draftId: string) => {
    const confirmed = confirm("Are you sure you want to delete this draft?");
    if (!confirmed) return;

    try {
      await draftsApi.delete(draftId);
      toast.success("Draft deleted successfully!");
      await loadData();
      if (selectedDraft?.id === draftId) {
        setSelectedDraft(null);
      }
    } catch (error: any) {
      console.error("Delete draft error:", error);
      toast.error(error?.message || "Failed to delete draft");
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-slate-900 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto text-blue-600" />
          <p className="mt-4 text-slate-600 dark:text-slate-400">Loading drafts...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col bg-slate-50 dark:bg-slate-900">
      {/* Header */}
      <header className="h-16 bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 flex items-center justify-between px-8 flex-shrink-0">
        <div className="flex items-center gap-8">
          <Link to="/dashboard" className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center">
              <MailIcon className="w-5 h-5 text-white" />
            </div>
            <span className="text-lg font-bold text-slate-900 dark:text-white">CreatorPulse</span>
          </Link>

          <nav className="flex items-center gap-6">
            <Link to="/dashboard" className="text-sm font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white">
              Dashboard
            </Link>
            <Link to="/sources" className="text-sm font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white">
              Sources
            </Link>
            <Link to="/drafts" className="text-sm font-medium text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 pb-0.5">
              Drafts
            </Link>
          </nav>
        </div>

        <div className="flex items-center gap-4">
          <span className="text-sm text-slate-600 dark:text-slate-400">{user?.email}</span>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon">
                <Settings className="w-5 h-5" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
              <DropdownMenuLabel>Account Settings</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem>
                <User className="w-4 h-4 mr-2" />
                <span>Profile</span>
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => window.open('https://docs.creatorpulse.com', '_blank')}>
                <HelpCircle className="w-4 h-4 mr-2" />
                <span>Help & Documentation</span>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={logout} className="text-red-600 focus:text-red-600">
                <LogOut className="w-4 h-4 mr-2" />
                <span>Logout</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </header>

      {/* Toolbar */}
      <div className="bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 px-8 py-4 flex items-center justify-between flex-shrink-0">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Newsletter Drafts</h1>
          <p className="text-sm text-slate-600 dark:text-slate-400">AI-powered newsletters from your curated sources</p>
        </div>

        <div className="flex gap-3">
          <Button variant="outline" onClick={loadData} disabled={isLoading}>
            <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          <Button onClick={handleGenerateDraft} disabled={isGenerating || sourceCount === 0} className="bg-blue-600 hover:bg-blue-700 text-white">
            {isGenerating ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4 mr-2" />
                Generate New Draft
              </>
            )}
          </Button>
        </div>
      </div>

      {/* Main Content */}
      {drafts.length === 0 ? (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <FileText className="w-16 h-16 mx-auto text-slate-400 mb-4" />
            <h2 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">No Drafts Yet</h2>
            <p className="text-slate-600 dark:text-slate-400 mb-6">
              {sourceCount === 0
                ? "Add sources first, then generate your first AI-powered newsletter draft."
                : "Click 'Generate New Draft' to create your first newsletter from your sources."}
            </p>
            {sourceCount === 0 && (
              <Link to="/sources">
                <Button className="bg-blue-600 hover:bg-blue-700 text-white">
                  <Plus className="w-4 h-4 mr-2" />
                  Add Sources First
                </Button>
              </Link>
            )}
          </div>
        </div>
      ) : (
        <div className="flex-1 flex overflow-hidden">
          {/* Sidebar */}
          <div className="w-80 bg-white dark:bg-slate-800 border-r border-slate-200 dark:border-slate-700 flex flex-col">
            <div className="p-4 border-b border-slate-200 dark:border-slate-700">
              <h2 className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide">
                Your Drafts ({drafts.length})
              </h2>
            </div>

            <div className="flex-1 overflow-y-auto p-3 space-y-2">
              {drafts.map((draft) => (
                <div
                  key={draft.id}
                  className={`p-3 rounded-lg cursor-pointer transition-colors ${
                    selectedDraft?.id === draft.id
                      ? "bg-blue-50 dark:bg-blue-900/20 border-l-4 border-blue-600"
                      : "hover:bg-slate-50 dark:hover:bg-slate-700/50"
                  }`}
                  onClick={() => setSelectedDraft(draft)}
                >
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <h3 className="text-sm font-semibold text-slate-900 dark:text-white line-clamp-2 flex-1">
                      {draft.subject || "Untitled Draft"}
                    </h3>
                    <Badge variant={draft.status === "pending" ? "default" : "secondary"} className="text-xs shrink-0">
                      {draft.status}
                    </Badge>
                  </div>

                  <div className="flex items-center gap-3 text-xs text-slate-600 dark:text-slate-400">
                    <div className="flex items-center gap-1">
                      <Calendar className="w-3 h-3" />
                      <span>{new Date(draft.created_at).toLocaleDateString()}</span>
                    </div>
                    {draft.generation_time && (
                      <div className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        <span>{Math.round(draft.generation_time)}s</span>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Content Area - FULL WIDTH */}
          <div className="flex-1 flex flex-col bg-white dark:bg-slate-800 overflow-hidden">
            {selectedDraft ? (
              <>
                {/* Draft Header */}
                <div className="border-b border-slate-200 dark:border-slate-700 px-12 py-6 flex-shrink-0">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                      <Badge variant={selectedDraft.status === "pending" ? "default" : "secondary"}>
                        {selectedDraft.status}
                      </Badge>
                      <span className="text-xs text-slate-600 dark:text-slate-400">
                        {new Date(selectedDraft.created_at).toLocaleString()}
                      </span>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-red-600 hover:text-red-700 hover:bg-red-50"
                      onClick={() => handleDeleteDraft(selectedDraft.id)}
                    >
                      <Trash2 className="w-4 h-4 mr-2" />
                      Delete
                    </Button>
                  </div>

                  <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-4">
                    {selectedDraft.subject || "Untitled Draft"}
                  </h2>

                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handleRegenerateDraft}
                      disabled={isRegenerating || sourceCount === 0}
                    >
                      {isRegenerating ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          Regenerating...
                        </>
                      ) : (
                        <>
                          <RotateCcw className="w-4 h-4 mr-2" />
                          Regenerate
                        </>
                      )}
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        navigator.clipboard.writeText(selectedDraft.html_content || selectedDraft.plain_text_content || "");
                        toast.success("Content copied to clipboard!");
                      }}
                    >
                      <Copy className="w-4 h-4 mr-2" />
                      Copy
                    </Button>
                    <Button
                      size="sm"
                      onClick={handleSendDraft}
                      disabled={isSending}
                      className="bg-green-600 hover:bg-green-700 text-white"
                    >
                      {isSending ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          Sending...
                        </>
                      ) : (
                        <>
                          <Send className="w-4 h-4 mr-2" />
                          Send Newsletter
                        </>
                      )}
                    </Button>
                  </div>
                </div>

                {/* Draft Content - COMPLETELY FULL WIDTH NO CONSTRAINTS */}
                <div className="flex-1 overflow-y-auto px-12 py-8">
                  <div className="newsletter-content text-slate-900 dark:text-slate-100">
                    {selectedDraft.html_content ? (
                      <div dangerouslySetInnerHTML={{ __html: extractCleanContent(selectedDraft.html_content) }} />
                    ) : selectedDraft.plain_text_content ? (
                      <pre className="whitespace-pre-wrap font-sans text-base leading-relaxed">{selectedDraft.plain_text_content}</pre>
                    ) : (
                      <div className="text-center py-16">
                        <FileText className="w-12 h-12 mx-auto text-slate-400 mb-4" />
                        <p className="text-slate-600 dark:text-slate-400">No content available</p>
                      </div>
                    )}
                  </div>
                </div>
              </>
            ) : (
              <div className="flex-1 flex items-center justify-center">
                <div className="text-center">
                  <FileText className="w-16 h-16 mx-auto text-slate-400 mb-4" />
                  <p className="text-slate-600 dark:text-slate-400">Select a draft to preview</p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
