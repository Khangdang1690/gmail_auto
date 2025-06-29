// Instead of using FastAPI to respond to the query, you can directly use langchain.js
// and create `@/app/api/chat/route.ts` file and paste below code in the file.
// after creating the file, make sure to update the api in useChat() in the @/components/chat/Section.tsx folder

import { NextRequest, NextResponse } from 'next/server';
import { Message as VercelChatMessage } from 'ai';

import { ChatOpenAI } from '@langchain/openai';
import { PromptTemplate } from '@langchain/core/prompts';
// HttpResponseOutputParser is not available with current packages, using basic streaming instead
// import { HttpResponseOutputParser } from 'langchain/output_parsers';

export const runtime = 'edge';

const formatMessage = (message: VercelChatMessage) => {
  return `${message.role}: ${message.content}`;
};

const TEMPLATE = `You are a helpful assistant. Respond to all user input with clear, concise, and informative responses.

User: {input}
AI:
`;

/**
 * This handler initializes and calls a simple chain with a prompt,
 * chat model, and output parser. See the docs for more information:
 *
 * https://js.langchain.com/docs/guides/expression_language/cookbook#prompttemplate--llm--outputparser
 */
export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const messages = body.messages ?? [];
    const currentMessageContent = messages[messages.length - 1].content;
    const prompt = PromptTemplate.fromTemplate(TEMPLATE);

    /**
     * You can also try e.g.:
     *
     * import { ChatAnthropic } from "@langchain/anthropic";
     * const model = new ChatAnthropic({});
     *
     * See a full list of supported models at:
     * https://js.langchain.com/docs/modules/model_io/models/
     */
    const model = new ChatOpenAI({
      temperature: 0.8,
      model: 'gpt-3.5-turbo-0125',
    });

    /**
     * Simple chain without streaming parser for this example
     * For production use, consider installing the full langchain package
     * or implementing proper streaming
     */
    const chain = prompt.pipe(model);

    const response = await chain.invoke({
      input: currentMessageContent,
    });

    return NextResponse.json({ response: response.content });
  } catch (e: any) {
    return NextResponse.json({ error: e.message }, { status: e.status ?? 500 });
  }
}
