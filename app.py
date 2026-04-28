from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

# 从 gongkao_knowledge.txt 加载题目
def load_questions():
    questions = {
        "常识": [],
        "言语": [],
        "判断": [],
        "数量": [],
        "申论": []
    }
    try:
        with open("gongkao_knowledge.txt", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split("|")
                if len(parts) == 8:
                    q_type, title, optA, optB, optC, optD, answer, explain = parts
                    questions[q_type].append({
                        "题目": title,
                        "选项": [optA, optB, optC, optD],
                        "答案": answer,
                        "解析": explain
                    })
    except Exception as e:
        print(f"加载题目出错：{e}")
    return questions

QUESTIONS = load_questions()

# 全局状态
current_question = None
stats = {"total": 0, "correct": 0}
wrong_questions = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    global current_question, stats, wrong_questions
    data = request.get_json()
    if not data or 'msg' not in data:
        return jsonify({"content": "请输入你的问题"})
    
    msg = data['msg'].strip().upper()

    # 1. 处理用户答题
    if msg in ["A", "B", "C", "D"] and current_question:
        stats["total"] += 1
        if msg == current_question["答案"]:
            stats["correct"] += 1
            reply = f"✅ 回答正确！\n解析：{current_question['解析']}"
        else:
            wrong_questions.append(current_question)
            reply = f"❌ 回答错误！\n正确答案：{current_question['答案']}\n解析：{current_question['解析']}"
        current_question = None
        return jsonify({"content": reply})

    # 2. 查看错题本
    if "错题" in msg:
        if not wrong_questions:
            reply = "📚 错题本为空"
        else:
            reply = "📚 错题本\n"
            for i, q in enumerate(wrong_questions, 1):
                reply += f"{i}. {q['题目']} → 答案：{q['答案']}\n"
        return jsonify({"content": reply})

    # 3. 查看统计
    if "统计" in msg:
        reply = f"📊 答题统计\n总题数：{stats['total']}\n正确：{stats['correct']}\n错误：{len(wrong_questions)}"
        return jsonify({"content": reply})

    # 4. 按题型出题
    if "常识" in msg and QUESTIONS["常识"]:
        q = random.choice(QUESTIONS["常识"])
        current_question = q
        return jsonify({"content": f"【常识题】\n{q['题目']}\n" + "\n".join(q['选项'])})
    if "言语" in msg and QUESTIONS["言语"]:
        q = random.choice(QUESTIONS["言语"])
        current_question = q
        return jsonify({"content": f"【言语题】\n{q['题目']}\n" + "\n".join(q['选项'])})
    if "判断" in msg and QUESTIONS["判断"]:
        q = random.choice(QUESTIONS["判断"])
        current_question = q
        return jsonify({"content": f"【判断题】\n{q['题目']}\n" + "\n".join(q['选项'])})
    if "数量" in msg and QUESTIONS["数量"]:
        q = random.choice(QUESTIONS["数量"])
        current_question = q
        return jsonify({"content": f"【数量题】\n{q['题目']}\n" + "\n".join(q['选项'])})
    if "申论" in msg and QUESTIONS["申论"]:
        q = random.choice(QUESTIONS["申论"])
        current_question = q
        return jsonify({"content": f"【申论题】\n{q['题目']}\n" + "\n".join(q['选项'])})

    # 5. 默认欢迎语
    return jsonify({
        "content": "👋 欢迎使用公考刷题助手\n\n支持题型：常识、言语、判断、数量、申论\n\n使用方式：输入题型名开始刷题，输入A/B/C/D作答，输入“统计”查看成绩，输入“错题”查看错题本"
    })

if __name__ == '__main__':
    app.run(debug=True)