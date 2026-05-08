from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

# 从 gongkao_knowledge.txt 读取题目
knowledge = []
with open("gongkao_knowledge.txt", "r", encoding="utf-8") as f:
    content = f.read().strip().split("\n\n")  # 按空行分割题目
    for idx, q in enumerate(content, 1):
        if q.strip():
            knowledge.append({
                "id": idx,
                "title": q.split("\n")[0],  # 第一行作为题目标题
                "content": q
            })

# 全局统计和错题本
user_stats = {
    "total": 0,
    "correct": 0,
    "wrong": 0
}
wrong_questions = []

@app.route('/')
def index():
    return render_template("index.html", knowledge=knowledge, stats=user_stats)

# 随机获取题目
@app.route('/random-q')
def random_q():
    q = random.choice(knowledge)
    return jsonify(q)

# 提交答案判分
@app.route('/check-ans', methods=['POST'])
def check_ans():
    data = request.get_json()
    qid = int(data["qid"])
    user_ans = data["ans"].strip().upper()

    # 找到题目
    target = next((item for item in knowledge if item["id"] == qid), None)
    if not target:
        return jsonify({"correct": False})

    # 提取正确答案（格式：...答案：A）
    content = target["content"]
    if "答案：" in content:
        right_ans = content.split("答案：")[1].strip()[0]
    else:
        right_ans = ""

    is_correct = (user_ans == right_ans)

    # 更新统计
    user_stats["total"] += 1
    if is_correct:
        user_stats["correct"] += 1
    else:
        user_stats["wrong"] += 1
        if target not in wrong_questions:
            wrong_questions.append(target)

    return jsonify({
        "correct": is_correct,
        "right_ans": right_ans,
        "explain": content
    })

if __name__ == '__main__':
    app.run(debug=True)